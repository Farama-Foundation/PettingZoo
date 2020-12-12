import numpy as np
import scipy.spatial.distance as ssd
from gym import spaces
from gym.utils import seeding
from .._utils import Agent
import cv2


class Archea(Agent):

    def __init__(self, idx, radius, n_sensors, sensor_range, speed_features=True):
        self._idx = idx
        self._radius = radius
        self._n_sensors = n_sensors
        self._sensor_range = sensor_range
        # Number of observation coordinates from each sensor
        self._sensor_obscoord = 4
        if speed_features:
            self._sensor_obscoord += 3
        self._obscoord_from_sensors = self._n_sensors * self._sensor_obscoord
        self._obs_dim = self._obscoord_from_sensors + 2  # +1 for type, +1 for id

        self._position = None
        self._velocity = None
        # Sensors
        angles_K = np.linspace(0., 2. * np.pi, self._n_sensors + 1)[:-1]
        sensor_vecs_K_2 = np.c_[np.cos(angles_K), np.sin(angles_K)]
        self._sensors = sensor_vecs_K_2

    @property
    def observation_space(self):
        return spaces.Box(low=np.float32(-10), high=np.float32(10), shape=(self._obs_dim,), dtype=np.float32)

    @property
    def action_space(self):
        return spaces.Box(low=np.float32(-1), high=np.float32(1), shape=(2,), dtype=np.float32)

    @property
    def position(self):
        assert self._position is not None
        return self._position

    @property
    def velocity(self):
        assert self._velocity is not None
        return self._velocity

    def set_position(self, x_2):
        assert x_2.shape == (2,)
        self._position = x_2

    def set_velocity(self, v_2):
        assert v_2.shape == (2,)
        self._velocity = v_2

    @property
    def sensors(self):
        assert self._sensors is not None
        return self._sensors

    def sensed(self, objx_N_2, same=False):
        """Whether `obj` would be sensed by the pursuers"""
        relpos_obj_N_2 = objx_N_2 - np.expand_dims(self.position, 0)
        sensorvals_K_N = self.sensors.dot(relpos_obj_N_2.T)
        sensorvals_K_N[(sensorvals_K_N < 0) | (sensorvals_K_N > self._sensor_range) | ((
            relpos_obj_N_2**2).sum(axis=1)[None, :] - sensorvals_K_N**2 > self._radius**2)] = np.inf
        if same:
            sensorvals_K_N[:, self._idx - 1] = np.inf
        return sensorvals_K_N


class MAWaterWorld():

    def __init__(self, n_pursuers=5, n_evaders=5, n_coop=2, n_poison=10, radius=0.015,
                 obstacle_radius=0.2, initial_obstacle_coord=np.array([0.5, 0.5]), evader_speed=0.01,
                 poison_speed=0.01, n_sensors=30, sensor_range=0.2, action_scale=0.01,
                 poison_reward=-1., food_reward=10., encounter_reward=.01, control_penalty=-.5,
                 local_ratio=1.0, speed_features=True, max_cycles=500, **kwargs):
        """
            n_pursuers: number of pursuing archea
            n_evaders: number of evaading archea
            n_coop: number of agent collisions needed to mark as caught
            n_poison: number of poison objects
            radius: pursuer archea radius
            obstacle_radius: radius of obstacle object
            initial_obstacle_coord: starting coordinate of obstacle object
            evader_speed: evading archea speed
            poison_speed: speed of poison object
            n_sensors: number of sensor dendrites on all archea
            sensor_range: length of sensor dendrite on all archea
            action_scale: scaling factor applied to all input actions
            poison_reward: reward for pursuer consuming a poison object
            food_reward: reward for pursuers consuming an evading archea
            encounter_reward: reward for a pursuer colliding with an evading archea
            control_penalty: reward added to pursuer in each step
            local_ratio: proportion of reward allocated locally vs distributed among all agents
            speed_features: toggles whether archea sensors detect speed of other objects
            max_cycles: number of frames before environment automatically ends
        """
        self.n_pursuers = n_pursuers
        self.n_evaders = n_evaders
        self.n_coop = n_coop
        self.n_poison = n_poison
        self.obstacle_radius = obstacle_radius
        self.initial_obstacle_coord = initial_obstacle_coord
        self.poison_speed = poison_speed
        self.radius = radius
        self.evader_speed = evader_speed
        self.n_sensors = n_sensors
        self.sensor_range = np.ones(self.n_pursuers) * sensor_range
        self.action_scale = action_scale
        self.poison_reward = poison_reward
        self.food_reward = food_reward
        self.control_penalty = control_penalty
        self.encounter_reward = encounter_reward
        self.last_rewards = [np.float64(0) for _ in range(self.n_pursuers)]
        self.control_rewards = [0 for _ in range(self.n_pursuers)]
        self.last_dones = [False for _ in range(self.n_pursuers)]
        self.last_obs = [None for _ in range(self.n_pursuers)]

        self.n_obstacles = 1
        self.local_ratio = local_ratio
        self._speed_features = speed_features
        self.max_cycles = max_cycles
        self.seed()
        # TODO: Look into changing hardcoded radius ratios
        self._pursuers = [
            Archea(pursuer_idx + 1, self.radius, self.n_sensors, self.sensor_range[pursuer_idx],
                   speed_features=self._speed_features) for pursuer_idx in range(self.n_pursuers)
        ]
        self._evaders = [
            Archea(evader_idx + 1, self.radius * 2, self.n_pursuers,
                   self.sensor_range.mean() / 2)
            for evader_idx in range(self.n_evaders)
        ]
        self._poisons = [
            Archea(poison_idx + 1, self.radius * 3 / 4, self.n_poison, 0) for poison_idx in range(self.n_poison)
        ]

        self.num_agents = self.n_pursuers
        self.action_space = [agent.action_space for agent in self._pursuers]
        self.observation_space = [
            agent.observation_space for agent in self._pursuers]

        self.renderOn = False

        self.cycle_time = 0.8
        self.frames = 0
        self.reset()

    def close(self):
        if self.renderOn:
            cv2.destroyAllWindows()
            cv2.waitKey(1)

    @property
    def agents(self):
        return self._pursuers

    def get_param_values(self):
        return self.__dict__

    def seed(self, seed=None):
        self.np_random, seed = seeding.np_random(seed)
        return [seed]

    def _generate_coord(self, radius):
        coord = self.np_random.rand(2)
        # Create random coordinate that avoids obstacles
        while ssd.cdist(coord[None, :], self.obstacle_coords) <= radius * 2 + self.obstacle_radius:
            coord = self.np_random.rand(2)
        return coord

    def reset(self):
        self.frames = 0
        # Initialize obstacles
        if self.initial_obstacle_coord is None:
            # Generate obstacle positions in range [0, 1)
            self.obstacle_coords = self.np_random.rand(self.n_obstacles, 2)
        else:
            self.obstacle_coords = self.initial_obstacle_coord[None, :]
        # Set each obstacle's velocity to 0
        # TODO: remove if obstacles should never move
        self.obstacle_speeds = np.zeros((self.n_obstacles, 2))

        # Initialize pursuers
        for pursuer in self._pursuers:
            pursuer.set_position(self._generate_coord(pursuer._radius))
            pursuer.set_velocity(np.zeros(2))

        # Initialize evaders
        for evader in self._evaders:
            evader.set_position(self._generate_coord(evader._radius))
            # Generate both velocity components from range [-self.evader_speed, self.evader_speed) 
            evader.set_velocity(
                (self.np_random.rand(2) - 0.5) * 2 * self.evader_speed)

        # Initialize poisons
        for poison in self._poisons:
            poison.set_position(self._generate_coord(poison._radius))
            # Generate both velocity components from range [-self.poison_speed, self.poison_speed) 
            poison.set_velocity((self.np_random.rand(2) - 0.5) * 2 * self.poison_speed)

        rewards = np.zeros(self.n_pursuers)
        sensorfeatures_Np_K_O, is_colliding_ev_Np_Ne, is_colliding_po_Np_Npo, rewards = self.collision_handling_subroutine(
            rewards, True)
        obs_list = self.observe_list(
            sensorfeatures_Np_K_O, is_colliding_ev_Np_Ne, is_colliding_po_Np_Npo)
        self.last_rewards = [np.float64(0) for _ in range(self.n_pursuers)]
        self.control_rewards = [0 for _ in range(self.n_pursuers)]
        self.last_dones = [False for _ in range(self.n_pursuers)]
        self.last_obs = obs_list

        return obs_list[0]

    def _caught(self, is_colliding_N1_N2, n_coop):
        """ Check whether collision results in catching the object

        This is because you need `n_coop` agents to collide with the object to actually catch it
        """
        # number of N1 colliding with given N2
        n_collisions_N2 = is_colliding_N1_N2.sum(axis=0)
        is_caught_cN2 = np.where(n_collisions_N2 >= n_coop)[0]

        # number of N2 colliding with given N1
        who_collisions_N1_cN2 = is_colliding_N1_N2[:, is_caught_cN2]
        who_caught_cN1 = np.where(who_collisions_N1_cN2 >= 1)[0]

        return is_caught_cN2, who_caught_cN1

    def _closest_dist(self, closest_obj_idx_Np_K, sensorvals_Np_K_N):
        """Closest distances according to `idx`"""
        sensorvals = []
        for inp in range(self.n_pursuers):
            sensorvals.append(sensorvals_Np_K_N[inp, ...][np.arange(self.n_sensors),
                                                          closest_obj_idx_Np_K[inp, ...]])
        return np.c_[sensorvals]

    def _extract_speed_features(self, objv_N_2, closest_obj_idx_N_K, sensedmask_obj_Np_K):
        sensorvals = []
        for pursuer in self._pursuers:
            sensorvals.append(
                pursuer.sensors.dot((objv_N_2 - np.expand_dims(pursuer.velocity, 0)).T))
        sensed_objspeed_Np_K_N = np.c_[sensorvals]

        sensed_objspeedfeatures_Np_K = np.zeros(
            (self.n_pursuers, self.n_sensors))

        sensorvals = []
        for inp in range(self.n_pursuers):
            sensorvals.append(sensed_objspeed_Np_K_N[inp, :, :][np.arange(self.n_sensors),
                                                                closest_obj_idx_N_K[inp, :]])
        sensed_objspeedfeatures_Np_K[sensedmask_obj_Np_K] = np.c_[
            sensorvals][sensedmask_obj_Np_K]

        return sensed_objspeedfeatures_Np_K

    def collision_handling_subroutine(self, rewards, is_last):
        # Stop pursuers upon hitting a wall
        for pursuer in self._pursuers:
            clipped_coord = np.clip(pursuer.position, 0, 1)
            clipped_velocity = pursuer.velocity
            # If x or y position gets clipped, set x or y velocity to 0 respectively
            clipped_velocity[pursuer.position != clipped_coord] = 0
            # Save clipped velocity and position
            pursuer.set_velocity(clipped_velocity)
            pursuer.set_position(clipped_coord)

        def rebound_particles(particles, n):
            collisions_particle_obstacle = np.zeros(n)
            # Particles rebound on hitting an obstacle
            for idx, particle in enumerate(particles):
                obstacle_distance = ssd.cdist(np.expand_dims(
                    particle.position, 0), self.obstacle_coords)
                is_colliding = obstacle_distance <= particle._radius + self.obstacle_radius
                collisions_particle_obstacle[idx] = is_colliding.sum()
                if collisions_particle_obstacle[idx] > 0:
                    # Rebound the particle that collided with an obstacle
                    velocity_scale = pursuer._radius + self.obstacle_radius - \
                        ssd.euclidean(particle.position, self.obstacle_coords)
                    pos_diff = particle.position - self.obstacle_coords[0]
                    new_pos = particle.position + velocity_scale * pos_diff
                    particle.set_position(new_pos)

                    collision_normal = particle.position - self.obstacle_coords[0]
                    # project current velocity onto collision normal
                    current_vel = particle.velocity
                    proj_numer = np.dot(current_vel, collision_normal)
                    cllsn_mag = np.dot(collision_normal, collision_normal)
                    proj_vel = (proj_numer / cllsn_mag) * collision_normal
                    perp_vel = current_vel - proj_vel
                    total_vel = perp_vel - proj_vel
                    particle.set_velocity(total_vel)

        rebound_particles(self._pursuers, self.n_pursuers)


        if is_last:
            rebound_particles(self._evaders, self.n_evaders)
            rebound_particles(self._poisons, self.n_poison)

        # Find collisions
        positions_pursuer = np.array([pursuer.position for pursuer in self._pursuers])
        positions_evader = np.array([evader.position for evader in self._evaders])
        positions_poison = np.array([poison.position for poison in self._poisons])

        # Evaders
        distances_pursuer_evader = ssd.cdist(positions_pursuer, positions_evader)
        # Generate n_evaders x n_pursuers matrix of boolean values for collisions
        collisions_pursuer_evader = distances_pursuer_evader <= np.asarray([
            pursuer._radius + evader._radius for pursuer in self._pursuers
            for evader in self._evaders
        ]).reshape(self.n_pursuers, self.n_evaders)

        # num_collisions depends on how many needed to catch an evader
        caught_evaders, evader_catching_pursuers = self._caught(
            collisions_pursuer_evader, self.n_coop)

        # Poisons
        distances_pursuer_poison = ssd.cdist(positions_pursuer, positions_poison)
        collisions_pursuer_poison = distances_pursuer_poison <= np.asarray([
            pursuer._radius + poison._radius for pursuer in self._pursuers
            for poison in self._poisons
        ]).reshape(self.n_pursuers, self.n_poison)


        caught_poisons, poison_catching_pursuers = self._caught(
            collisions_pursuer_poison, 1)

        # Find sensed objects
        # Obstacles
        sensorvals_pursuer_obstacle = np.array(
            [pursuer.sensed(self.obstacle_coords) for pursuer in self._pursuers])

        # Evaders
        sensorvals_pursuer_evader = np.array(
            [pursuer.sensed(positions_evader) for pursuer in self._pursuers])

        # Poison
        sensorvals_pursuer_poison = np.array(
            [pursuer.sensed(positions_poison) for pursuer in self._pursuers])

        # Allies
        sensorvals_pursuer_pursuer = np.array(
            [pursuer.sensed(positions_pursuer, same=True) for pursuer in self._pursuers])


        
        # dist features
        def sensor_features(sensorvals):    
            closest_idx_array = np.argmin(sensorvals, axis=2)
            closest_distances = self._closest_dist(
                closest_idx_array, sensorvals)
            infinite_mask = np.isfinite(closest_distances)
            sensed_distances = np.zeros(
                (self.n_pursuers, self.n_sensors))
            sensed_distances[infinite_mask] = closest_distances[infinite_mask]
            return sensed_distances, closest_idx_array, infinite_mask

        obstacle_distance_features, _, _  = sensor_features(sensorvals_pursuer_obstacle)
        evader_distance_features, closest_evader_idx, evader_mask  = sensor_features(sensorvals_pursuer_evader)
        poison_distance_features, closest_poison_idx, poison_mask = sensor_features(sensorvals_pursuer_poison)
        pursuer_distance_features, closest_pursuer_idx, pursuer_mask = sensor_features(sensorvals_pursuer_pursuer)

        # speed features
        pursuers_speed = np.array(
            [pursuer.velocity for pursuer in self._pursuers])
        evaders_speed = np.array([evader.velocity for evader in self._evaders])
        poisons_speed = np.array([poison.velocity for poison in self._poisons])

        # Evaders

        evader_speed_features = self._extract_speed_features(evaders_speed,
                                                                   closest_evader_idx,
                                                                   evader_mask)
        # Poison
        poison_speed_features = self._extract_speed_features(poisons_speed,
                                                                   closest_poison_idx,
                                                                   poison_mask)
        # Allies
        pursuer_speed_features = self._extract_speed_features(pursuers_speed,
                                                                   closest_pursuer_idx,
                                                                   pursuer_mask)

        # Process collisions
        # If object collided with required number of players, reset its position and velocity
        # Effectively the same as removing it and adding it back
        if caught_evaders.size:
            for evader_idx in caught_evaders:
                self._evaders[evader_idx].set_position(
                    self._generate_coord(self._evaders[evader_idx]._radius))
                # Generate both velocity components from range [-self.evader_speed, self.evader_speed) 
                self._evaders[evader_idx].set_velocity(
                    (self.np_random.rand(2,) - 0.5) * 2 * self.evader_speed)

        if caught_poisons.size:
            for poison_idx in caught_poisons:
                self._poisons[poison_idx].set_position(
                    self._generate_coord(self._poisons[poison_idx]._radius))
                # Generate both velocity components from range [-self.poison_speed, self.poison_speed) 
                self._poisons[poison_idx].set_velocity(
                    (self.np_random.rand(2,) - 0.5) * 2 * self.poison_speed)

        evader_encounters, evader_encounter_matrix = self._caught(
            collisions_pursuer_evader, 1)
        # Update reward based on these collisions
        rewards[evader_catching_pursuers] += self.food_reward
        rewards[poison_catching_pursuers] += self.poison_reward
        rewards[evader_encounter_matrix] += self.encounter_reward

        # Add features together
        if self._speed_features:
            sensorfeatures = np.c_[obstacle_distance_features, evader_distance_features,
                                          evader_speed_features, poison_distance_features,
                                          poison_speed_features, pursuer_distance_features,
                                          pursuer_speed_features]
        else:
            sensorfeatures = np.c_[obstacle_distance_Features, evader_distance_feature,
                                          poison_distance_feature, pursuer_distance_feature]

        return sensorfeatures, collisions_pursuer_evader, collisions_pursuer_poison, rewards

    def observe_list(self, sensor_feature, is_colliding_ev, is_colliding_po):
        obslist = []
        for pursuer_idx in range(self.n_pursuers):
            obslist.append(
                np.concatenate([
                    sensor_feature[pursuer_idx, ...].ravel(), [
                        float((is_colliding_ev[pursuer_idx, :]).sum() > 0), float((
                            is_colliding_po[pursuer_idx, :]).sum() > 0)
                    ]
                ]))
        return obslist

    def step(self, action, agent_id, is_last):

        action = np.asarray(action)
        action = action.reshape(2)

        action = action * self.action_scale

        p = self._pursuers[agent_id]
        p.set_velocity(p.velocity + action)
        p.set_position(p.position + self.cycle_time * p.velocity)

        if is_last:
            for evader in self._evaders:
                # Move objects
                evader.set_position(
                    evader.position + self.cycle_time * evader.velocity)
                # Bounce object if it hits a wall
                for i in range(len(evader.position)):
                    if evader.position[i] >= 1 or evader.position[i] <= 0:
                        evader.position[i] = np.clip(evader.position[i], 0, 1)
                        evader.velocity[i] = -1 * evader.velocity[i]

            for poison in self._poisons:
                # Move objects
                poison.set_position(
                    poison.position + self.cycle_time * poison.velocity)
                # Bounce object if it hits a wall
                for i in range(len(poison.position)):
                    if poison.position[i] >= 1 or poison.position[i] <= 0:
                        poison.position[i] = np.clip(poison.position[i], 0, 1)
                        poison.velocity[i] = -1 * poison.velocity[i]

        control_reward = self.control_penalty * (action**2).sum()
        self.control_rewards = (control_reward / self.n_pursuers) * np.ones(self.n_pursuers) * (1 - self.local_ratio)
        self.control_rewards[agent_id] += control_reward * self.local_ratio

        if is_last:
            rewards = np.zeros(self.n_pursuers)
            sensorfeatures_Np_K_O, is_colliding_ev_Np_Ne, is_colliding_po_Np_Npo, rewards = self.collision_handling_subroutine(
                rewards, is_last)
            obs_list = self.observe_list(
                sensorfeatures_Np_K_O, is_colliding_ev_Np_Ne, is_colliding_po_Np_Npo)
            self.last_obs = obs_list

            local_reward = rewards
            global_reward = local_reward.mean()
            self.last_rewards = local_reward * self.local_ratio + global_reward * (1 - self.local_ratio)

            self.frames += 1

        return self.observe(agent_id)

    def observe(self, agent):
        return np.array(self.last_obs[agent], dtype=np.float32)

    def render(self, mode='human', screen_size=900, rate=5):
        if not self.renderOn and mode == "human":
            self.renderOn = True
            cv2.startWindowThread()
        img = np.empty((screen_size, screen_size, 3), dtype=np.uint8)
        img[...] = 255
        # Obstacles
        for iobs, obstaclex_2 in enumerate(self.obstacle_coords):
            assert obstaclex_2.shape == (2,)
            color = (128, 128, 0)
            cv2.circle(img,
                       tuple((obstaclex_2 * screen_size).astype(int)),
                       int(self.obstacle_radius * screen_size), color, -1, lineType=cv2.CV_32S)
        # Pursuers
        for pursuer in self._pursuers:
            for k in range(pursuer._n_sensors):
                color = (0, 0, 0)
                cv2.line(img,
                         tuple((pursuer.position * screen_size).astype(int)),
                         tuple(((pursuer.position + pursuer._sensor_range * pursuer.sensors[k]) * screen_size).astype(int)), color, 1, lineType=cv2.CV_32S)
                cv2.circle(img,
                           tuple((pursuer.position * screen_size).astype(int)),
                           int(pursuer._radius * screen_size), (255, 0, 0), -1, lineType=cv2.CV_32S)
        # Evaders
        for evader in self._evaders:
            color = (0, 255, 0)
            cv2.circle(img,
                       tuple((evader.position * screen_size).astype(int)),
                       int(evader._radius * screen_size), color, -1, lineType=cv2.CV_32S)

        # Poison
        for poison in self._poisons:
            color = (0, 0, 255)
            cv2.circle(img,
                       tuple((poison.position * screen_size).astype(int)),
                       int(poison._radius * screen_size), color, -1, lineType=cv2.CV_32S)

        opacity = 0.4
        bg = np.ones((screen_size, screen_size, 3), dtype=np.uint8) * 255
        cv2.addWeighted(bg, opacity, img, 1 - opacity, 0, img)
        cv2.imshow('Waterworld', img)
        cv2.waitKey(rate)
        return np.asarray(img)[..., ::-1] if mode == "rgb_array" else None
