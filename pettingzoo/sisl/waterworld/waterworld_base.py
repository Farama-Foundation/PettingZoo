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
        self._obs_dim = self._obscoord_from_sensors + 2  # + 1  #2 for type, 1 for id

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
                 obstacle_radius=0.2, obstacle_loc=np.array([0.5, 0.5]), ev_speed=0.01,
                 poison_speed=0.01, n_sensors=30, sensor_range=0.2, action_scale=0.01,
                 poison_reward=-1., food_reward=10., encounter_reward=.01, control_penalty=-.5,
                 local_ratio=1.0, speed_features=True, max_frames=500, **kwargs):
        """
            n_pursuers: number of pursuing archea
            n_evaders: number of evaading archea
            n_coop: number of agent collisions needed to mark as caught
            n_poison: number of poison objects
            radius: pursuer archea radius
            obstacle_radius: radius of obstacle object
            obstacle_loc: coordinate of obstacle object
            ev_speed: evading archea speed
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
            max_frames: number of frames before environment automatically ends
        """
        self.n_pursuers = n_pursuers
        self.n_evaders = n_evaders
        self.n_coop = n_coop
        self.n_poison = n_poison
        self.obstacle_radius = obstacle_radius
        self.obstacle_loc = obstacle_loc
        self.poison_speed = poison_speed
        self.radius = radius
        self.ev_speed = ev_speed
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
        self.max_frames = max_frames
        self.seed()
        self._pursuers = [
            Archea(npu + 1, self.radius, self.n_sensors, self.sensor_range[npu],
                   speed_features=self._speed_features) for npu in range(self.n_pursuers)
        ]
        self._evaders = [
            Archea(nev + 1, self.radius * 2, self.n_pursuers,
                   self.sensor_range.mean() / 2)
            for nev in range(self.n_evaders)
        ]
        self._poisons = [
            Archea(npo + 1, self.radius * 3 / 4, self.n_poison, 0) for npo in range(self.n_poison)
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
    def timestep_limit(self):
        return 1000

    @property
    def agents(self):
        return self._pursuers

    def get_param_values(self):
        return self.__dict__

    def seed(self, seed=None):
        self.np_random, seed_ = seeding.np_random(seed)
        return [seed_]

    def _respawn(self, objx_2, radius):
        while ssd.cdist(objx_2[None, :], self.obstaclesx_No_2) <= radius * 2 + self.obstacle_radius:
            objx_2 = self.np_random.rand(2)
        return objx_2

    def reset(self):
        self._timesteps = 0
        self.frames = 0
        # Initialize obstacles
        if self.obstacle_loc is None:
            self.obstaclesx_No_2 = self.np_random.rand(self.n_obstacles, 2)
        else:
            self.obstaclesx_No_2 = self.obstacle_loc[None, :]
        self.obstaclesv_No_2 = np.zeros((self.n_obstacles, 2))

        # Initialize pursuers
        for pursuer in self._pursuers:
            pursuer.set_position(self.np_random.rand(2))
            # Avoid spawning where the obstacles lie
            pursuer.set_position(self._respawn(
                pursuer.position, pursuer._radius))
            pursuer.set_velocity(np.zeros(2))

        # Initialize evaders
        for evader in self._evaders:
            evader.set_position(self.np_random.rand(2))
            evader.set_position(self._respawn(evader.position, evader._radius))
            evader.set_velocity(
                (self.np_random.rand(2) - 0.5) * self.ev_speed)

        # Initialize poisons
        for poison in self._poisons:
            poison.set_position(self.np_random.rand(2))
            poison.set_position(self._respawn(poison.position, poison._radius))
            poison.set_velocity((self.np_random.rand(2) - 0.5) * self.ev_speed)

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

    @property
    def is_terminal(self):
        if self._timesteps >= self.timestep_limit:
            return True
        return False

    def _caught(self, is_colliding_N1_N2, n_coop):
        """ Checke whether collision results in catching the object

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
        # Players stop on hitting a wall
        for npu, pursuer in enumerate(self._pursuers):
            clippedx_2 = np.clip(pursuer.position, 0, 1)
            vel_2 = pursuer.velocity
            vel_2[pursuer.position != clippedx_2] = 0
            pursuer.set_velocity(vel_2)
            pursuer.set_position(clippedx_2)

        obstacle_coll_Np = np.zeros(self.n_pursuers)
        # Particles rebound on hitting an obstacle
        for npu, pursuer in enumerate(self._pursuers):
            distfromobst_No = ssd.cdist(np.expand_dims(
                pursuer.position, 0), self.obstaclesx_No_2)
            is_colliding_No = distfromobst_No <= pursuer._radius + self.obstacle_radius
            obstacle_coll_Np[npu] = is_colliding_No.sum()
            if obstacle_coll_Np[npu] > 0:
                velocity_scale = pursuer._radius + self.obstacle_radius - \
                    ssd.euclidean(pursuer.position, self.obstaclesx_No_2)
                pos_diff = pursuer.position - self.obstaclesx_No_2[0]
                new_pos = pursuer.position + velocity_scale * pos_diff
                pursuer.set_position(new_pos)

                collision_normal = pursuer.position - self.obstaclesx_No_2[0]
                # project current velocity onto collision normal
                current_vel = pursuer.velocity
                proj_numer = np.dot(current_vel, collision_normal)
                cllsn_mag = np.dot(collision_normal, collision_normal)
                proj_vel = (proj_numer / cllsn_mag) * collision_normal
                perp_vel = current_vel - proj_vel
                total_vel = perp_vel - proj_vel
                pursuer.set_velocity(total_vel)

        if is_last:
            obstacle_coll_Ne = np.zeros(self.n_evaders)
            for nev, evader in enumerate(self._evaders):
                distfromobst_No = ssd.cdist(np.expand_dims(
                    evader.position, 0), self.obstaclesx_No_2)
                is_colliding_No = distfromobst_No <= evader._radius + self.obstacle_radius
                obstacle_coll_Ne[nev] = is_colliding_No.sum()
                if obstacle_coll_Ne[nev] > 0:
                    velocity_scale = evader._radius + self.obstacle_radius - \
                        ssd.euclidean(evader.position, self.obstaclesx_No_2)
                    pos_diff = evader.position - self.obstaclesx_No_2[0]
                    evader.set_position(
                        evader.position + velocity_scale * pos_diff)

                    collision_normal = evader.position - \
                        self.obstaclesx_No_2[0]
                    # project current velocity onto collision normal
                    current_vel = evader.velocity
                    proj_numer = np.dot(current_vel, collision_normal)
                    cllsn_mag = np.dot(collision_normal, collision_normal)
                    proj_vel = (proj_numer / cllsn_mag) * collision_normal
                    perp_vel = current_vel - proj_vel
                    total_vel = perp_vel - proj_vel
                    evader.set_velocity(total_vel)

            obstacle_coll_Npo = np.zeros(self.n_poison)
            for npo, poison in enumerate(self._poisons):
                distfromobst_No = ssd.cdist(np.expand_dims(
                    poison.position, 0), self.obstaclesx_No_2)
                is_colliding_No = distfromobst_No <= poison._radius + self.obstacle_radius
                obstacle_coll_Npo[npo] = is_colliding_No.sum()
                if obstacle_coll_Npo[npo] > 0:
                    velocity_scale = poison._radius + self.obstacle_radius - \
                        ssd.euclidean(poison.position, self.obstaclesx_No_2)
                    pos_diff = poison.position - self.obstaclesx_No_2[0]
                    poison.set_position(
                        poison.position + velocity_scale * pos_diff)

                    collision_normal = poison.position - \
                        self.obstaclesx_No_2[0]
                    # project current velocity onto collision normal
                    current_vel = poison.velocity
                    proj_numer = np.dot(current_vel, collision_normal)
                    cllsn_mag = np.dot(collision_normal, collision_normal)
                    proj_vel = (proj_numer / cllsn_mag) * collision_normal
                    perp_vel = current_vel - proj_vel
                    total_vel = perp_vel - proj_vel
                    poison.set_velocity(total_vel)

        # Find collisions
        pursuersx_Np_2 = np.array(
            [pursuer.position for pursuer in self._pursuers])
        evadersx_Ne_2 = np.array([evader.position for evader in self._evaders])
        poisonx_Npo_2 = np.array([poison.position for poison in self._poisons])

        # Evaders
        evdists_Np_Ne = ssd.cdist(pursuersx_Np_2, evadersx_Ne_2)
        is_colliding_ev_Np_Ne = evdists_Np_Ne <= np.asarray([
            pursuer._radius + evader._radius for pursuer in self._pursuers
            for evader in self._evaders
        ]).reshape(self.n_pursuers, self.n_evaders)

        # num_collisions depends on how many needed to catch an evader
        ev_caught, which_pursuer_caught_ev = self._caught(
            is_colliding_ev_Np_Ne, self.n_coop)

        # Poisons
        podists_Np_Npo = ssd.cdist(pursuersx_Np_2, poisonx_Npo_2)
        is_colliding_po_Np_Npo = podists_Np_Npo <= np.asarray([
            pursuer._radius + poison._radius for pursuer in self._pursuers
            for poison in self._poisons
        ]).reshape(self.n_pursuers, self.n_poison)
        po_caught, which_pursuer_caught_po = self._caught(
            is_colliding_po_Np_Npo, 1)

        # Find sensed objects
        # Obstacles
        sensorvals_Np_K_No = np.array(
            [pursuer.sensed(self.obstaclesx_No_2) for pursuer in self._pursuers])

        # Evaders
        sensorvals_Np_K_Ne = np.array(
            [pursuer.sensed(evadersx_Ne_2) for pursuer in self._pursuers])

        # Poison
        sensorvals_Np_K_Npo = np.array(
            [pursuer.sensed(poisonx_Npo_2) for pursuer in self._pursuers])

        # Allies
        sensorvals_Np_K_Np = np.array(
            [pursuer.sensed(pursuersx_Np_2, same=True) for pursuer in self._pursuers])

        # dist features
        closest_ob_idx_Np_K = np.argmin(sensorvals_Np_K_No, axis=2)
        closest_ob_dist_Np_K = self._closest_dist(
            closest_ob_idx_Np_K, sensorvals_Np_K_No)
        sensedmask_ob_Np_K = np.isfinite(closest_ob_dist_Np_K)
        sensed_obdistfeatures_Np_K = np.zeros(
            (self.n_pursuers, self.n_sensors))
        sensed_obdistfeatures_Np_K[sensedmask_ob_Np_K] = closest_ob_dist_Np_K[sensedmask_ob_Np_K]
        # Evaders
        closest_ev_idx_Np_K = np.argmin(sensorvals_Np_K_Ne, axis=2)
        closest_ev_dist_Np_K = self._closest_dist(
            closest_ev_idx_Np_K, sensorvals_Np_K_Ne)
        sensedmask_ev_Np_K = np.isfinite(closest_ev_dist_Np_K)
        sensed_evdistfeatures_Np_K = np.zeros(
            (self.n_pursuers, self.n_sensors))
        sensed_evdistfeatures_Np_K[sensedmask_ev_Np_K] = closest_ev_dist_Np_K[sensedmask_ev_Np_K]
        # Poison
        closest_po_idx_Np_K = np.argmin(sensorvals_Np_K_Npo, axis=2)
        closest_po_dist_Np_K = self._closest_dist(
            closest_po_idx_Np_K, sensorvals_Np_K_Npo)
        sensedmask_po_Np_K = np.isfinite(closest_po_dist_Np_K)
        sensed_podistfeatures_Np_K = np.zeros(
            (self.n_pursuers, self.n_sensors))
        sensed_podistfeatures_Np_K[sensedmask_po_Np_K] = closest_po_dist_Np_K[sensedmask_po_Np_K]
        # Allies
        closest_pu_idx_Np_K = np.argmin(sensorvals_Np_K_Np, axis=2)
        closest_pu_dist_Np_K = self._closest_dist(
            closest_pu_idx_Np_K, sensorvals_Np_K_Np)
        sensedmask_pu_Np_K = np.isfinite(closest_pu_dist_Np_K)
        sensed_pudistfeatures_Np_K = np.zeros(
            (self.n_pursuers, self.n_sensors))
        sensed_pudistfeatures_Np_K[sensedmask_pu_Np_K] = closest_pu_dist_Np_K[sensedmask_pu_Np_K]

        # speed features
        pursuersv_Np_2 = np.array(
            [pursuer.velocity for pursuer in self._pursuers])
        evadersv_Ne_2 = np.array([evader.velocity for evader in self._evaders])
        poisonv_Npo_2 = np.array([poison.velocity for poison in self._poisons])

        # Evaders

        sensed_evspeedfeatures_Np_K = self._extract_speed_features(evadersv_Ne_2,
                                                                   closest_ev_idx_Np_K,
                                                                   sensedmask_ev_Np_K)
        # Poison
        sensed_pospeedfeatures_Np_K = self._extract_speed_features(poisonv_Npo_2,
                                                                   closest_po_idx_Np_K,
                                                                   sensedmask_po_Np_K)
        # Allies
        sensed_puspeedfeatures_Np_K = self._extract_speed_features(pursuersv_Np_2,
                                                                   closest_pu_idx_Np_K,
                                                                   sensedmask_pu_Np_K)

        # Process collisions
        # If object collided with required number of players, reset its position and velocity
        # Effectively the same as removing it and adding it back
        if ev_caught.size:
            for evcaught in ev_caught:
                self._evaders[evcaught].set_position(self.np_random.rand(2))
                self._evaders[evcaught].set_position(
                    self._respawn(self._evaders[evcaught].position, self._evaders[evcaught]
                                  ._radius))
                self._evaders[evcaught].set_velocity(
                    (self.np_random.rand(2,) - 0.5) * self.ev_speed)

        if po_caught.size:
            for pocaught in po_caught:
                self._poisons[pocaught].set_position(self.np_random.rand(2))
                self._poisons[pocaught].set_position(
                    self._respawn(self._poisons[pocaught].position, self._poisons[pocaught]
                                  ._radius))
                self._poisons[pocaught].set_velocity(
                    (self.np_random.rand(2,) - 0.5) * self.poison_speed)

        ev_encounters, which_pursuer_encounterd_ev = self._caught(
            is_colliding_ev_Np_Ne, 1)
        # Update reward based on these collisions
        rewards[which_pursuer_caught_ev] += self.food_reward
        rewards[which_pursuer_caught_po] += self.poison_reward
        rewards[which_pursuer_encounterd_ev] += self.encounter_reward

        # Add features together
        if self._speed_features:
            sensorfeatures_Np_K_O = np.c_[sensed_obdistfeatures_Np_K, sensed_evdistfeatures_Np_K,
                                          sensed_evspeedfeatures_Np_K, sensed_podistfeatures_Np_K,
                                          sensed_pospeedfeatures_Np_K, sensed_pudistfeatures_Np_K,
                                          sensed_puspeedfeatures_Np_K]
        else:
            sensorfeatures_Np_K_O = np.c_[sensed_obdistfeatures_Np_K, sensed_evdistfeatures_Np_K,
                                          sensed_podistfeatures_Np_K, sensed_pudistfeatures_Np_K]

        return sensorfeatures_Np_K_O, is_colliding_ev_Np_Ne, is_colliding_po_Np_Npo, rewards

    def observe_list(self, sensor_feature, is_colliding_ev, is_colliding_po):
        obslist = []
        for inp in range(self.n_pursuers):
            obslist.append(
                np.concatenate([
                    sensor_feature[inp, ...].ravel(), [
                        float((is_colliding_ev[inp, :]).sum() > 0), float((
                            is_colliding_po[inp, :]).sum() > 0)
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

        self.control_rewards[agent_id] = self.control_penalty * (action**2).sum()

        if is_last:
            rewards = np.zeros(self.n_pursuers)
            sensorfeatures_Np_K_O, is_colliding_ev_Np_Ne, is_colliding_po_Np_Npo, rewards = self.collision_handling_subroutine(
                rewards, is_last)
            obs_list = self.observe_list(
                sensorfeatures_Np_K_O, is_colliding_ev_Np_Ne, is_colliding_po_Np_Npo)
            self.last_obs = obs_list

            local_reward = rewards + np.array(self.control_rewards)
            global_reward = local_reward.mean()
            self.last_rewards = local_reward * self.local_ratio + global_reward * (1 - self.local_ratio)

            self.control_rewards = [0 for _ in range(self.n_pursuers)]

        self.dones = [self.is_terminal for _ in range(self.n_pursuers)]

        self._timesteps += 1
        self.frames += 1
        return self.observe(agent_id)

    def observe(self, agent):
        return np.array(self.last_obs[agent], dtype=np.float32)

    def render(self, screen_size=900, rate=5, mode='human'):
        if not self.renderOn:
            self.renderOn = True
            cv2.startWindowThread()
        img = np.empty((screen_size, screen_size, 3), dtype=np.uint8)
        img[...] = 255
        # Obstacles
        for iobs, obstaclex_2 in enumerate(self.obstaclesx_No_2):
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
        return np.asarray(img)[..., ::-1]
