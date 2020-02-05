import glob
import os
from os.path import join
from subprocess import call

import matplotlib.animation as animation
import matplotlib.pyplot as plt
import numpy as np
from gym import spaces
from gym.utils import seeding
from matplotlib.patches import Rectangle

from six.moves import xrange
from .utils import agent_utils
from .utils.agent_layer import AgentLayer
from .utils.controllers import RandomPolicy, SingleActionPolicy
from .utils import two_d_maps

#################################################################
# Implements an Evade Pursuit Problem in 2D
#################################################################

class Pursuit():    

    def __init__(self, **kwargs):
        """
        In evade purusit a set of pursuers must 'tag' a set of evaders
        Required arguments:

        Optional arguments:
        - Ally layer: list of pursuers
        Opponent layer: list of evaders
        Ally controller: stationary policy of ally pursuers
        Ally controller: stationary policy of opponent evaders
        map_matrix: the map on which agents interact
        catchr: reward for 'tagging' a single evader
        caughtr: reward for getting 'tagged' by a pursuer
        train_pursuit: flag indicating if we are simulating pursuers or evaders
        initial_config: dictionary of form
            initial_config['allies']: the initial ally confidguration (matrix)
            initial_config['opponents']: the initial opponent confidguration (matrix)
        """

        self.sample_maps = kwargs.pop('sample_maps', False)

        # self.map_pool = map_pool
        # map_matrix = map_pool[0]
        self.xs = kwargs.pop('xs', 16)
        self.ys = kwargs.pop('ys', 16)
        xs = self.xs
        ys = self.ys
        self.map_matrix = two_d_maps.rectangle_map(self.xs, self.ys)

        self._reward_mech = kwargs.pop('reward_mech', 'local')

        self.n_evaders = kwargs.pop('n_evaders', 30)
        self.n_pursuers = kwargs.pop('n_pursuers', 8)
        self.num_agents = self.n_pursuers
        self.agent_ids = list(range(self.num_agents))

        self.obs_range = kwargs.pop('obs_range', 7)  # can see 7 grids around them by default
        #assert self.obs_range % 2 != 0, "obs_range should be odd"
        self.obs_offset = int((self.obs_range - 1) / 2)

        self.flatten = kwargs.pop('flatten', True)

        self.pursuers = agent_utils.create_agents(self.n_pursuers, self.map_matrix, self.obs_range,
                                                  flatten=self.flatten)
        self.evaders = agent_utils.create_agents(self.n_evaders, self.map_matrix, self.obs_range,
                                                 flatten=self.flatten)

        self.pursuer_layer = kwargs.pop('ally_layer', AgentLayer(xs, ys, self.pursuers))
        self.evader_layer = kwargs.pop('opponent_layer', AgentLayer(xs, ys, self.evaders))

        self.layer_norm = kwargs.pop('layer_norm', 10)

        self.n_catch = kwargs.pop('n_catch', 2)

        self.random_opponents = kwargs.pop('random_opponents', False)
        self.max_opponents = kwargs.pop('max_opponents', 10)

        n_act_purs = self.pursuer_layer.get_nactions(0)
        n_act_ev = self.evader_layer.get_nactions(0)

        self.evader_controller = kwargs.pop('evader_controller', RandomPolicy(n_act_purs))
        self.pursuer_controller = kwargs.pop('pursuer_controller', RandomPolicy(n_act_ev))
        # self.evader_controller = kwargs.pop('evader_controller', SingleActionPolicy(4))
        # self.pursuer_controller = kwargs.pop('pursuer_controller', SingleActionPolicy(4))

        self.current_agent_layer = np.zeros((xs, ys), dtype=np.int32)

        self.catchr = kwargs.pop('catchr', 0.01)
        self.caughtr = kwargs.pop('caughtr', -0.01)

        self.term_pursuit = kwargs.pop('term_pursuit', 5.0)
        self.term_evade = kwargs.pop('term_evade', -5.0)

        self.urgency_reward = kwargs.pop('urgency_reward', 0.0)

        self.include_id = kwargs.pop('include_id', True)

        self.ally_actions = np.zeros(n_act_purs, dtype=np.int32)
        self.opponent_actions = np.zeros(n_act_ev, dtype=np.int32)

        self.train_pursuit = kwargs.pop('train_pursuit', True)

        if self.train_pursuit:
            self.low = np.array([0.0 for i in range(3 * self.obs_range**2)])
            self.high = np.array([1.0 for i in range(3 * self.obs_range**2)])
            if self.include_id:
                self.low = np.append(self.low, 0.0)
                self.high = np.append(self.high, 1.0)
            self.action_space = [spaces.Discrete(n_act_purs) for _ in range(self.n_pursuers)]
            if self.flatten:
                self.observation_space = [spaces.Box(self.low, self.high) for _ in range(self.n_pursuers)]
            else:
                self.observation_space = [spaces.Box(low=-np.inf, high=np.inf,
                                                    shape=(4, self.obs_range, self.obs_range)) for _ in range(self.n_pursuers)]
            self.local_obs = np.zeros(
                (self.n_pursuers, 4, self.obs_range, self.obs_range))  # Nagents X 3 X xsize X ysize
            self.act_dims = [n_act_purs for i in range(self.n_pursuers)]
        else:
            self.low = np.array([0.0 for i in range(3 * self.obs_range**2)])
            self.high = np.array([1.0 for i in range(3 * self.obs_range**2)])
            if self.include_id:
                np.append(self.low, 0.0)
                np.append(self.high, 1.0)
            self.action_space = [spaces.Discrete(n_act_ev) for _ in range(self.n_evaders)]
            if self.flatten:
                self.observation_space = [spaces.Box(self.low, self.high) for _ in range(self.n_evaders)]
            else:
                self.observation_space = [spaces.Box(low=-np.inf, high=np.inf,
                                                    shape=(4, self.obs_range, self.obs_range)) for _ in range(self.n_evaders)]
            self.local_obs = np.zeros(
                (self.n_evaders, 4, self.obs_range, self.obs_range))  # Nagents X 3 X xsize X ysize
            self.act_dims = [n_act_purs for i in range(self.n_evaders)]
        self.pursuers_gone = np.array([False for i in range(self.n_pursuers)])
        self.evaders_gone = np.array([False for i in range(self.n_evaders)])

        self.initial_config = kwargs.pop('initial_config', {})

        self.surround = kwargs.pop('surround', True)

        self.constraint_window = kwargs.pop('constraint_window', 1.0)

        self.curriculum_remove_every = kwargs.pop('curriculum_remove_every', 500)
        self.curriculum_constrain_rate = kwargs.pop('curriculum_constrain_rate', 0.0)
        self.curriculum_turn_off_shaping = kwargs.pop('curriculum_turn_off_shaping', np.inf)

        self.surround_mask = np.array([[-1, 0], [1, 0], [0, 1], [0, -1]])

        self.model_state = np.zeros((4,) + self.map_matrix.shape, dtype=np.float32)
        
    def close(self):
        pass

    #################################################################
    # The functions below are the interface with MultiAgentSiulator #
    #################################################################

    @property
    def agents(self):
        return self.pursuers

    @property
    def reward_mech(self):
        return self._reward_mech

    def seed(self, seed=None):
        self.np_random, seed_ = seeding.np_random(seed)
        return [seed_]

    def get_param_values(self):
        return self.__dict__

    def reset(self):
        #print "Check:", self.n_evaders, self.n_pursuers, self.catchr
        self.pursuers_gone.fill(False)
        self.evaders_gone.fill(False)
        if self.random_opponents:
            if self.train_pursuit:
                self.n_evaders = self.np_random.randint(1, self.max_opponents)
            else:
                self.n_pursuers = self.np_random.randint(1, self.max_opponents)
        if self.sample_maps:
            self.map_matrix = self.map_pool[np.random.randint(len(self.map_pool))]

        x_window_start = np.random.uniform(0.0, 1.0 - self.constraint_window)
        y_window_start = np.random.uniform(0.0, 1.0 - self.constraint_window)
        xlb, xub = int(self.xs * x_window_start), int(self.xs *
                                                      (x_window_start + self.constraint_window))
        ylb, yub = int(self.ys * y_window_start), int(self.ys *
                                                      (y_window_start + self.constraint_window))
        constraints = [[xlb, xub], [ylb, yub]]

        self.pursuers = agent_utils.create_agents(self.n_pursuers, self.map_matrix, self.obs_range,
                                                  randinit=True, constraints=constraints)
        self.pursuer_layer = AgentLayer(self.xs, self.ys, self.pursuers)

        self.evaders = agent_utils.create_agents(self.n_evaders, self.map_matrix, self.obs_range,
                                                 randinit=True, constraints=constraints)
        self.evader_layer = AgentLayer(self.xs, self.ys, self.evaders)

        self.model_state[0] = self.map_matrix
        self.model_state[1] = self.pursuer_layer.get_state_matrix()
        self.model_state[2] = self.evader_layer.get_state_matrix()
        if self.train_pursuit:
            return self.collect_obs(self.pursuer_layer, self.pursuers_gone)
        else:
            return self.collect_obs(self.evader_layer, self.evaders_gone)

    def step(self, actions):
        """
            Step the system forward. Actions is an iterable of action indecies.
        """
        rewards = self.reward()

        if self.train_pursuit:
            agent_layer = self.pursuer_layer
            opponent_layer = self.evader_layer
            opponent_controller = self.evader_controller
            gone_flags = self.pursuers_gone
        else:
            agent_layer = self.evader_layer
            opponent_layer = self.pursuer_layer
            opponent_controller = self.pursuer_controller
            gone_flags = self.evaders_gone

        # move allies
        if isinstance(actions, list) or isinstance(actions, np.ndarray):
            # move all agents
            for i, a in enumerate(actions):
                agent_layer.move_agent(i, a)
        else:
            # ravel it up
            act_idxs = np.unravel_index(actions, self.act_dims)
            for i, a in enumerate(act_idxs):
                agent_layer.move_agent(i, a)

        # move opponents
        for i in range(opponent_layer.n_agents()):
            # controller input should be an observation, but doesn't matter right now
            action = opponent_controller.act(self.model_state)
            opponent_layer.move_agent(i, action)

        # model state always has form: map, purusers, opponents, current agent id
        self.model_state[0] = self.map_matrix
        self.model_state[1] = self.pursuer_layer.get_state_matrix()
        self.model_state[2] = self.evader_layer.get_state_matrix()

        # remove agents that are caught
        ev_remove, pr_remove, pursuers_who_remove = self.remove_agents()

        obslist = self.collect_obs(agent_layer, gone_flags)

        # add caught rewards
        rewards += self.term_pursuit * pursuers_who_remove
        # urgency reward to speed up catching
        rewards += self.urgency_reward

        done = self.is_terminal
        done_list = [done] * self.n_pursuers

        if self.reward_mech == 'global':
            return obslist, [rewards.mean()] * self.n_pursuers, done_list, {'removed': ev_remove}
        
        return obslist, rewards, done_list, [] # info: {'removed': ev_remove} 

    def update_curriculum(self, itr):
        self.constraint_window += self.curriculum_constrain_rate  # 0 to 1 in 500 iterations
        self.constraint_window = np.clip(self.constraint_window, 0.0, 1.0)
        # remove agents every 10 iter?
        if itr != 0 and itr % self.curriculum_remove_every == 0 and self.n_pursuers > 4:
            self.n_evaders -= 1
            self.n_pursuers -= 1
        if itr > self.curriculum_turn_off_shaping:
            self.catchr = 0.0

    def render(self, plt_delay=0.03):
        self.renderOn = True
        plt.matshow(self.model_state[0].T, cmap=plt.get_cmap('Greys'), fignum=1)
        for i in range(self.pursuer_layer.n_agents()):
            x, y = self.pursuer_layer.get_position(i)
            plt.plot(x, y, "r*", markersize=12)
            if self.train_pursuit:
                ax = plt.gca()
                ofst = self.obs_range / 2.0
                ax.add_patch(
                    Rectangle((x - ofst, y - ofst), self.obs_range, self.obs_range, alpha=0.5,
                              facecolor="#FF9848"))
        for i in range(self.evader_layer.n_agents()):
            x, y = self.evader_layer.get_position(i)
            plt.plot(x, y, "b*", markersize=12)
            if not self.train_pursuit:
                ax = plt.gca()
                ofst = self.obs_range / 2.0
                ax.add_patch(
                    Rectangle((x - ofst, y - ofst), self.obs_range, self.obs_range, alpha=0.5,
                              facecolor="#009ACD"))
        plt.pause(plt_delay)
        plt.clf()

    def animate(self, act_fn, nsteps, file_name, rate=1.5, verbose=False):
        """
            Save an animation to an mp4 file.
        """
        plt.figure(0)
        # run sim loop
        o = self.reset()
        file_path = "/".join(file_name.split("/")[0:-1])
        temp_name = join(file_path, "temp_0.png")
        # generate .pngs
        self.save_image(temp_name)
        removed = 0
        for i in range(nsteps):
            a = act_fn(o)
            o, r, done, info = self.step(a)
            temp_name = join(file_path, "temp_" + str(i + 1) + ".png")
            self.save_image(temp_name)
            removed += info['removed']
            if verbose:
                print(r, info)
            if done:
                break
        if verbose:
            print("Total removed:", removed)
        # use ffmpeg to create .pngs to .mp4 movie
        ffmpeg_cmd = "ffmpeg -framerate " + str(rate) + " -i " + join(
            file_path, "temp_%d.png") + " -c:v libx264 -pix_fmt yuv420p " + file_name
        call(ffmpeg_cmd.split())
        # clean-up by removing .pngs
        map(os.remove, glob.glob(join(file_path, "temp_*.png")))

    def save_image(self, file_name):
        plt.cla()
        plt.matshow(self.model_state[0].T, cmap=plt.get_cmap('Greys'), fignum=0)
        x, y = self.pursuer_layer.get_position(0)
        plt.plot(x, y, "r*", markersize=12)
        for i in range(self.pursuer_layer.n_agents()):
            x, y = self.pursuer_layer.get_position(i)
            plt.plot(x, y, "r*", markersize=12)
            if self.train_pursuit:
                ax = plt.gca()
                ofst = self.obs_range / 2.0
                ax.add_patch(
                    Rectangle((x - ofst, y - ofst), self.obs_range, self.obs_range, alpha=0.5,
                              facecolor="#FF9848"))
        for i in range(self.evader_layer.n_agents()):
            x, y = self.evader_layer.get_position(i)
            plt.plot(x, y, "b*", markersize=12)
            if not self.train_pursuit:
                ax = plt.gca()
                ofst = self.obs_range / 2.0
                ax.add_patch(
                    Rectangle((x - ofst, y - ofst), self.obs_range, self.obs_range, alpha=0.5,
                              facecolor="#009ACD"))

        xl, xh = -self.obs_offset - 1, self.xs + self.obs_offset + 1
        yl, yh = -self.obs_offset - 1, self.ys + self.obs_offset + 1
        plt.xlim([xl, xh])
        plt.ylim([yl, yh])
        plt.axis('off')
        plt.savefig(file_name, dpi=200)

    def reward(self):
        """
        Computes the joint reward for pursuers
        """
        # rewarded for each tagged evader
        ps = self.pursuer_layer.get_state_matrix()  # pursuer positions
        es = self.evader_layer.get_state_matrix()  # evader positions
        # tag reward
        #tagged = (ps > 0) * es
        #rewards = [
        #    self.catchr *
        #    tagged[self.pursuer_layer.get_position(i)[0], self.pursuer_layer.get_position(i)[1]]
        #    for i in xrange(self.n_pursuers)
        #]
        # proximity reward
        rewards = [
            self.catchr * np.sum(es[np.clip(
                self.pursuer_layer.get_position(i)[0] + self.surround_mask[:, 0], 0, self.xs - 1
            ), np.clip(
                self.pursuer_layer.get_position(i)[1] + self.surround_mask[:, 1], 0, self.ys - 1)])
            for i in range(self.n_pursuers)
        ]
        return np.array(rewards)

    @property
    def is_terminal(self):
        #ev = self.evader_layer.get_state_matrix()  # evader positions
        #if np.sum(ev) == 0.0:
        if self.evader_layer.n_agents() == 0:
            return True
        return False

    def update_ally_controller(self, controller):
        self.ally_controller = controller

    def update_opponent_controller(self, controller):
        self.opponent_controller = controller

    def n_agents(self):
        return self.pursuer_layer.n_agents()

    def collect_obs(self, agent_layer, gone_flags):
        obs = []
        nage = 0
        for i in range(self.n_agents()):
            if gone_flags[i]:
                obs.append(None)
            else:
                o = self.collect_obs_by_idx(agent_layer, nage)
                obs.append(o)
                nage += 1
        return obs

    def collect_obs_by_idx(self, agent_layer, agent_idx):
        # returns a flattened array of all the observations
        n = agent_layer.n_agents()
        self.local_obs[agent_idx][0].fill(1.0 / self.layer_norm)  # border walls set to -0.1?
        xp, yp = agent_layer.get_position(agent_idx)

        xlo, xhi, ylo, yhi, xolo, xohi, yolo, yohi = self.obs_clip(xp, yp)

        self.local_obs[agent_idx, 0:3, xolo:xohi, yolo:yohi] = np.abs(
            self.model_state[0:3, xlo:xhi, ylo:yhi]) / self.layer_norm
        self.local_obs[agent_idx, 3, self.obs_range // 2, self.obs_range // 2] = float(
            agent_idx) / self.n_agents()
        if self.flatten:
            o = self.local_obs[agent_idx][0:3].flatten()
            if self.include_id:
                o = np.append(o, float(agent_idx) / self.n_agents())
            return o
        # reshape output from (C, H, W) to (H, W, C)
        #return self.local_obs[agent_idx]
        return np.rollaxis(self.local_obs[agent_idx], 0, 3)

    def obs_clip(self, x, y):
        # :( this is a mess, beter way to do the slicing? (maybe np.ix_)
        xld = x - self.obs_offset
        xhd = x + self.obs_offset
        yld = y - self.obs_offset
        yhd = y + self.obs_offset
        xlo, xhi, ylo, yhi = (np.clip(xld, 0, self.xs - 1), np.clip(xhd, 0, self.xs - 1),
                              np.clip(yld, 0, self.ys - 1), np.clip(yhd, 0, self.ys - 1))
        xolo, yolo = abs(np.clip(xld, -self.obs_offset, 0)), abs(np.clip(yld, -self.obs_offset, 0))
        xohi, yohi = xolo + (xhi - xlo), yolo + (yhi - ylo)
        return xlo, xhi + 1, ylo, yhi + 1, xolo, xohi + 1, yolo, yohi + 1

    def remove_agents(self):
        """
        Remove agents that are caught. Return tuple (n_evader_removed, n_pursuer_removed, purs_sur)
        purs_sur: bool array, which pursuers surrounded an evader
        """
        n_pursuer_removed = 0
        n_evader_removed = 0
        removed_evade = []
        removed_pursuit = []

        ai = 0
        rems = 0
        xpur, ypur = np.nonzero(self.model_state[1])
        purs_sur = np.zeros(self.n_pursuers, dtype=np.bool)
        for i in range(self.n_evaders):
            if self.evaders_gone[i]:
                continue
            x, y = self.evader_layer.get_position(ai)
            if self.surround:
                pos_that_catch = self.surround_mask + self.evader_layer.get_position(ai)
                truths = np.array(
                    [np.equal([xi, yi], pos_that_catch).all(axis=1) for xi, yi in zip(xpur, ypur)])
                if np.sum(truths.any(axis=0)) == self.need_to_surround(x, y):
                    removed_evade.append(ai - rems)
                    self.evaders_gone[i] = True
                    rems += 1
                    tt = truths.any(axis=1)
                    for j in range(self.n_pursuers):
                        xpp, ypp = self.pursuer_layer.get_position(j)
                        tes = np.concatenate((xpur[tt], ypur[tt])).reshape(2, len(xpur[tt]))
                        tem = tes.T == np.array([xpp, ypp])
                        if np.any(np.all(tem, axis=1)):
                            purs_sur[j] = True
                ai += 1
            else:
                if self.model_state[1, x, y] >= self.n_catch:
                    # add prob remove?
                    removed_evade.append(ai - rems)
                    self.evaders_gone[i] = True
                    rems += 1
                    for j in range(self.n_pursuers):
                        xpp, ypp = self.pursuer_layer.get_position(j)
                        if xpp == x and ypp == y:
                            purs_sur[j] = True
                ai += 1

        ai = 0
        for i in range(self.pursuer_layer.n_agents()):
            if self.pursuers_gone[i]:
                continue
            x, y = self.pursuer_layer.get_position(i)
            # can remove pursuers probabilitcally here?
        for ridx in removed_evade:
            self.evader_layer.remove_agent(ridx)
            n_evader_removed += 1
        for ridx in removed_pursuit:
            self.pursuer_layer.remove_agent(ridx)
            n_pursuer_removed += 1
        return n_evader_removed, n_pursuer_removed, purs_sur

    def need_to_surround(self, x, y):
        """
            Compute the number of surrounding grid cells in x,y position that are open
            (no wall or obstacle)
        """
        tosur = 4
        if x == 0 or x == (self.xs - 1):
            tosur -= 1
        if y == 0 or y == (self.ys - 1):
            tosur -= 1
        neighbors = self.surround_mask + np.array([x, y])
        for n in neighbors:
            xn, yn = n
            if not 0 < xn < self.xs or not 0 < yn < self.ys:
                continue
            if self.model_state[0][xn, yn] == -1:
                tosur -= 1
        return tosur



    #################################################################  
    ################## Model Based Methods ##########################
    #################################################################  

    def idx2state(self, idx):
        # return the index of a state
        # assume single evader for now
        pos = np.unravel_index(idx, [self.xs, self.ys] * (self.n_evaders + self.n_pursuers), 'F')
        s = np.zeros(self.model_state.shape)
        
        return s


    def n_states(self):
        return (self.xs * self.ys) ** (self.n_evaders + self.n_pursuers)
