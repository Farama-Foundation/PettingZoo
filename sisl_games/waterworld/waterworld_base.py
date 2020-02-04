import numpy as np
import scipy.spatial.distance as ssd
from gym import spaces
from gym.utils import seeding

from .. import Agent


class Archea(Agent):

    def __init__(self, idx, radius, n_sensors, sensor_range, addid=True, speed_features=True):
        self._idx = idx
        self._radius = radius
        self._n_sensors = n_sensors
        self._sensor_range = sensor_range
        # Number of observation coordinates from each sensor
        self._sensor_obscoord = 4
        if speed_features:
            self._sensor_obscoord += 3
        self._obscoord_from_sensors = self._n_sensors * self._sensor_obscoord
        self._obs_dim = self._obscoord_from_sensors + 2  #+ 1  #2 for type, 1 for id
        if addid:
            self._obs_dim += 1

        self._position = None
        self._velocity = None
        # Sensors
        angles_K = np.linspace(0., 2. * np.pi, self._n_sensors + 1)[:-1]
        sensor_vecs_K_2 = np.c_[np.cos(angles_K), np.sin(angles_K)]
        self._sensors = sensor_vecs_K_2

    @property
    def observation_space(self):
        return spaces.Box(low=-10, high=10, shape=(self._obs_dim,))

    @property
    def action_space(self):
        return spaces.Box(low=-1, high=1, shape=(2,))

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
                 reward_mech='local', addid=True, speed_features=True, **kwargs):
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

        self.n_obstacles = 1
        self._reward_mech = reward_mech
        self._addid = addid
        self._speed_features = speed_features
        self.seed()
        self._pursuers = [
            Archea(npu + 1, self.radius, self.n_sensors, self.sensor_range[npu], addid=self._addid,
                   speed_features=self._speed_features) for npu in range(self.n_pursuers)
        ]
        self._evaders = [
            Archea(nev + 1, self.radius * 2, self.n_pursuers, self.sensor_range.mean() / 2)
            for nev in range(self.n_evaders)
        ]
        self._poisons = [
            Archea(npo + 1, self.radius * 3 / 4, self.n_poison, 0) for npo in range(self.n_poison)
        ]
        
        self.num_agents = self.n_pursuers
        self.action_space = [agent.action_space for agent in self._pursuers]
        self.observation_space = [agent.observation_space for agent in self._pursuers]

    def close(self):
        pass

    @property
    def reward_mech(self):
        return self._reward_mech

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
            pursuer.set_position(self._respawn(pursuer.position, pursuer._radius))
            pursuer.set_velocity(np.zeros(2))

        # Initialize evaders
        for evader in self._evaders:
            evader.set_position(self.np_random.rand(2))
            evader.set_position(self._respawn(evader.position, evader._radius))
            evader.set_velocity((self.np_random.rand(2) - 0.5) * self.ev_speed)  # TODO policies

        # Initialize poisons
        for poison in self._poisons:
            poison.set_position(self.np_random.rand(2))
            poison.set_position(self._respawn(poison.position, poison._radius))
            poison.set_velocity((self.np_random.rand(2) - 0.5) * self.ev_speed)

        return self.step(np.zeros((self.n_pursuers, 2)))[0]

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

        sensed_objspeedfeatures_Np_K = np.zeros((self.n_pursuers, self.n_sensors))

        sensorvals = []
        for inp in range(self.n_pursuers):
            sensorvals.append(sensed_objspeed_Np_K_N[inp, :, :][np.arange(self.n_sensors),
                                                                closest_obj_idx_N_K[inp, :]])
        sensed_objspeedfeatures_Np_K[sensedmask_obj_Np_K] = np.c_[sensorvals][sensedmask_obj_Np_K]

        return sensed_objspeedfeatures_Np_K

    def step(self, action_Np2):
        action_Np2 = np.asarray(action_Np2)
        action_Np_2 = action_Np2.reshape((self.n_pursuers, 2))
        # Players
        actions_Np_2 = action_Np_2 * self.action_scale

        rewards = np.zeros((self.n_pursuers,))
        assert action_Np_2.shape == (self.n_pursuers, 2)

        for npu, pursuer in enumerate(self._pursuers):
            pursuer.set_velocity(pursuer.velocity + actions_Np_2[npu])
            pursuer.set_position(pursuer.position + pursuer.velocity)

        # Penalize large actions
        if self.reward_mech == 'global':
            rewards += self.control_penalty * (actions_Np_2**2).sum()
        else:
            rewards += self.control_penalty * (actions_Np_2**2).sum(axis=1)

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
            distfromobst_No = ssd.cdist(np.expand_dims(pursuer.position, 0), self.obstaclesx_No_2)
            is_colliding_No = distfromobst_No <= pursuer._radius + self.obstacle_radius
            obstacle_coll_Np[npu] = is_colliding_No.sum()
            if obstacle_coll_Np[npu] > 0:
                pursuer.set_velocity(-1 / 2 * pursuer.velocity)

        obstacle_coll_Ne = np.zeros(self.n_evaders)
        for nev, evader in enumerate(self._evaders):
            distfromobst_No = ssd.cdist(np.expand_dims(evader.position, 0), self.obstaclesx_No_2)
            is_colliding_No = distfromobst_No <= evader._radius + self.obstacle_radius
            obstacle_coll_Ne[nev] = is_colliding_No.sum()
            if obstacle_coll_Ne[nev] > 0:
                evader.set_velocity(-1 / 2 * evader.velocity)

        obstacle_coll_Npo = np.zeros(self.n_poison)
        for npo, poison in enumerate(self._poisons):
            distfromobst_No = ssd.cdist(np.expand_dims(poison.position, 0), self.obstaclesx_No_2)
            is_colliding_No = distfromobst_No <= poison._radius + self.obstacle_radius
            obstacle_coll_Npo[npo] = is_colliding_No.sum()
            if obstacle_coll_Npo[npo] > 0:
                poison.set_velocity(-1 * poison.velocity)

        # Find collisions
        pursuersx_Np_2 = np.array([pursuer.position for pursuer in self._pursuers])
        evadersx_Ne_2 = np.array([evader.position for evader in self._evaders])
        poisonx_Npo_2 = np.array([poison.position for poison in self._poisons])

        # Evaders
        evdists_Np_Ne = ssd.cdist(pursuersx_Np_2, evadersx_Ne_2)
        is_colliding_ev_Np_Ne = evdists_Np_Ne <= np.asarray([
            pursuer._radius + evader._radius for pursuer in self._pursuers
            for evader in self._evaders
        ]).reshape(self.n_pursuers, self.n_evaders)

        # num_collisions depends on how many needed to catch an evader
        ev_caught, which_pursuer_caught_ev = self._caught(is_colliding_ev_Np_Ne, self.n_coop)

        # Poisons
        podists_Np_Npo = ssd.cdist(pursuersx_Np_2, poisonx_Npo_2)
        is_colliding_po_Np_Npo = podists_Np_Npo <= np.asarray([
            pursuer._radius + poison._radius for pursuer in self._pursuers
            for poison in self._poisons
        ]).reshape(self.n_pursuers, self.n_poison)
        po_caught, which_pursuer_caught_po = self._caught(is_colliding_po_Np_Npo, 1)

        # Find sensed objects
        # Obstacles
        sensorvals_Np_K_No = np.array(
            [pursuer.sensed(self.obstaclesx_No_2) for pursuer in self._pursuers])

        # Evaders
        sensorvals_Np_K_Ne = np.array([pursuer.sensed(evadersx_Ne_2) for pursuer in self._pursuers])

        # Poison
        sensorvals_Np_K_Npo = np.array(
            [pursuer.sensed(poisonx_Npo_2) for pursuer in self._pursuers])

        # Allies
        sensorvals_Np_K_Np = np.array(
            [pursuer.sensed(pursuersx_Np_2, same=True) for pursuer in self._pursuers])

        # dist features
        closest_ob_idx_Np_K = np.argmin(sensorvals_Np_K_No, axis=2)
        closest_ob_dist_Np_K = self._closest_dist(closest_ob_idx_Np_K, sensorvals_Np_K_No)
        sensedmask_ob_Np_K = np.isfinite(closest_ob_dist_Np_K)
        sensed_obdistfeatures_Np_K = np.zeros((self.n_pursuers, self.n_sensors))
        sensed_obdistfeatures_Np_K[sensedmask_ob_Np_K] = closest_ob_dist_Np_K[sensedmask_ob_Np_K]
        # Evaders
        closest_ev_idx_Np_K = np.argmin(sensorvals_Np_K_Ne, axis=2)
        closest_ev_dist_Np_K = self._closest_dist(closest_ev_idx_Np_K, sensorvals_Np_K_Ne)
        sensedmask_ev_Np_K = np.isfinite(closest_ev_dist_Np_K)
        sensed_evdistfeatures_Np_K = np.zeros((self.n_pursuers, self.n_sensors))
        sensed_evdistfeatures_Np_K[sensedmask_ev_Np_K] = closest_ev_dist_Np_K[sensedmask_ev_Np_K]
        # Poison
        closest_po_idx_Np_K = np.argmin(sensorvals_Np_K_Npo, axis=2)
        closest_po_dist_Np_K = self._closest_dist(closest_po_idx_Np_K, sensorvals_Np_K_Npo)
        sensedmask_po_Np_K = np.isfinite(closest_po_dist_Np_K)
        sensed_podistfeatures_Np_K = np.zeros((self.n_pursuers, self.n_sensors))
        sensed_podistfeatures_Np_K[sensedmask_po_Np_K] = closest_po_dist_Np_K[sensedmask_po_Np_K]
        # Allies
        closest_pu_idx_Np_K = np.argmin(sensorvals_Np_K_Np, axis=2)
        closest_pu_dist_Np_K = self._closest_dist(closest_pu_idx_Np_K, sensorvals_Np_K_Np)
        sensedmask_pu_Np_K = np.isfinite(closest_pu_dist_Np_K)
        sensed_pudistfeatures_Np_K = np.zeros((self.n_pursuers, self.n_sensors))
        sensed_pudistfeatures_Np_K[sensedmask_pu_Np_K] = closest_pu_dist_Np_K[sensedmask_pu_Np_K]

        # speed features
        pursuersv_Np_2 = np.array([pursuer.velocity for pursuer in self._pursuers])
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

        ev_encounters, which_pursuer_encounterd_ev = self._caught(is_colliding_ev_Np_Ne, 1)
        # Update reward based on these collisions
        if self.reward_mech == 'global':
            rewards += (
                (len(ev_caught) * self.food_reward) + (len(po_caught) * self.poison_reward) +
                (len(ev_encounters) * self.encounter_reward))
        else:
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

        for evader in self._evaders:
            # Move objects
            evader.set_position(evader.position + evader.velocity)
            # Bounce object if it hits a wall
            if all(evader.position != np.clip(evader.position, 0, 1)):
                evader.set_velocity(-1 * evader.velocity)

        for poison in self._poisons:
            # Move objects
            poison.set_position(poison.position + poison.velocity)
            # Bounce object if it hits a wall
            if all(poison.position != np.clip(poison.position, 0, 1)):
                poison.set_velocity(-1 * poison.velocity)

        obslist = []
        for inp in range(self.n_pursuers):
            if self._addid:
                obslist.append(
                    np.concatenate([
                        sensorfeatures_Np_K_O[inp, ...].ravel(), [
                            float((is_colliding_ev_Np_Ne[inp, :]).sum() > 0), float((
                                is_colliding_po_Np_Npo[inp, :]).sum() > 0)
                        ], [inp + 1]
                    ]))
            else:
                obslist.append(
                    np.concatenate([
                        sensorfeatures_Np_K_O[inp, ...].ravel(), [
                            float((is_colliding_ev_Np_Ne[inp, :]).sum() > 0), float((
                                is_colliding_po_Np_Npo[inp, :]).sum() > 0)
                        ]
                    ]))

        assert all([
            obs.shape == agent.observation_space.shape for obs, agent in zip(obslist, self.agents)
        ])
        self._timesteps += 1
        done = self.is_terminal
        # info = dict(evcatches=len(ev_caught), pocatches=len(po_caught))
        info = {}
        return obslist, rewards, [done] * self.n_pursuers, [info] * self.n_pursuers

    def render(self, screen_size=800, rate=10, mode='human'):
        import cv2
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
                         tuple(((pursuer.position + pursuer._sensor_range * pursuer.sensors[k]) *
                                screen_size).astype(int)), color, 1, lineType=cv2.CV_32S)
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

