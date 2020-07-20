import glob
import os
from os.path import join
from subprocess import call

import numpy as np
from gym import spaces
from gym.utils import seeding


import pygame

from .utils import agent_utils
from .utils.agent_layer import AgentLayer
from .utils.controllers import RandomPolicy, SingleActionPolicy
from .utils import two_d_maps


class Pursuit():

    def __init__(self, seed=0, **kwargs):
        """
        In evade purusit a set of pursuers must 'tag' a set of evaders
        Required arguments:
            xs, ys: World size
            reward_mech: local or global reward mechanism
            n_evaders
            n_pursuers
            obs_range: how far each agent can see
        Optional arguments:
        Ally layer: list of pursuers
        Opponent layer: list of evaders
        pursuer controller: stationary policy of ally pursuers
        evader controller: stationary policy of opponent evaders

        catchr: reward for 'tagging' a single evader
        caughtr: reward for getting 'tagged' by a pursuer

        train_pursuit: flag indicating if we are simulating pursuers or evaders
        max_frames: after how many frames should the game end
        n_catch: how surrounded evader needs to be, before removal
        random_opponents: randomized number of evaders on reset
        max_opponents: maximum number of random evaders on reset
        freeze_evaders: toggle evaders move or not
        term_pursuit: reward for pursuer who catches an evader
        urgency_reward: reward added in each step
        train_pursuit: toggles whether pursuers are rewarded or evaders
        surround: toggles surround condition for evader removal
        constraint_window: window in which agents can randomly spawn
        """

        self.xs = kwargs.pop('xs', 16)
        self.ys = kwargs.pop('ys', 16)
        xs = self.xs
        ys = self.ys
        self.map_matrix = two_d_maps.rectangle_map(self.xs, self.ys)
        self.max_frames = kwargs.pop("max_frames", 500)
        self.seed(seed)

        self._reward_mech = kwargs.pop('reward_mech', 'local')

        self.n_evaders = kwargs.pop('n_evaders', 30)
        self.n_pursuers = kwargs.pop('n_pursuers', 8)
        self.num_agents = self.n_pursuers

        self.latest_reward_state = [0 for _ in range(self.num_agents)]
        self.latest_done_state = [False for _ in range(self.num_agents)]
        self.latest_obs = [None for _ in range(self.num_agents)]

        # can see 7 grids around them by default
        self.obs_range = kwargs.pop('obs_range', 7)
        # assert self.obs_range % 2 != 0, "obs_range should be odd"
        self.obs_offset = int((self.obs_range - 1) / 2)
        self.pursuers = agent_utils.create_agents(
            self.n_pursuers, self.map_matrix, self.obs_range, self.np_random)
        self.evaders = agent_utils.create_agents(
            self.n_evaders, self.map_matrix, self.obs_range, self.np_random)

        self.pursuer_layer = kwargs.pop(
            'ally_layer', AgentLayer(xs, ys, self.pursuers))
        self.evader_layer = kwargs.pop(
            'opponent_layer', AgentLayer(xs, ys, self.evaders))

        self.n_catch = kwargs.pop('n_catch', 2)

        self.random_opponents = kwargs.pop('random_opponents', False)
        self.max_opponents = kwargs.pop('max_opponents', 10)

        n_act_purs = self.pursuer_layer.get_nactions(0)
        n_act_ev = self.evader_layer.get_nactions(0)

        self.freeze_evaders = kwargs.pop('freeze_evaders', False)

        if self.freeze_evaders:
            self.evader_controller = kwargs.pop(
                'evader_controller', SingleActionPolicy(4))
            self.pursuer_controller = kwargs.pop(
                'pursuer_controller', SingleActionPolicy(4))
        else:
            self.evader_controller = kwargs.pop(
                'evader_controller', RandomPolicy(n_act_purs, self.np_random))
            self.pursuer_controller = kwargs.pop(
                'pursuer_controller', RandomPolicy(n_act_ev, self.np_random))

        self.current_agent_layer = np.zeros((xs, ys), dtype=np.int32)

        self.catchr = kwargs.pop('catchr', 0.01)
        self.caughtr = kwargs.pop('caughtr', -0.01)

        self.term_pursuit = kwargs.pop('term_pursuit', 5.0)

        self.urgency_reward = kwargs.pop('urgency_reward', 0.0)

        self.ally_actions = np.zeros(n_act_purs, dtype=np.int32)
        self.opponent_actions = np.zeros(n_act_ev, dtype=np.int32)

        self.train_pursuit = kwargs.pop('train_pursuit', True)

        max_agents_overlap = max(self.n_pursuers, self.n_evaders)
        obs_space = spaces.Box(low=0, high=max_agents_overlap, shape=(
            self.obs_range, self.obs_range, 3), dtype=np.float32)
        act_space = spaces.Discrete(n_act_purs)
        if self.train_pursuit:
            self.action_space = [act_space for _ in range(self.n_pursuers)]

            self.observation_space = [obs_space for _ in range(self.n_pursuers)]
            self.act_dims = [n_act_purs for i in range(self.n_pursuers)]
        else:
            self.action_space = [act_space for _ in range(self.n_evaders)]

            self.observation_space = [obs_space for _ in range(self.n_evaders)]
            self.act_dims = [n_act_purs for i in range(self.n_evaders)]
        self.pursuers_gone = np.array([False for i in range(self.n_pursuers)])
        self.evaders_gone = np.array([False for i in range(self.n_evaders)])

        self.surround = kwargs.pop('surround', True)

        self.constraint_window = kwargs.pop('constraint_window', 1.0)

        self.surround_mask = np.array([[-1, 0], [1, 0], [0, 1], [0, -1]])

        self.model_state = np.zeros(
            (4,) + self.map_matrix.shape, dtype=np.float32)
        self.renderOn = False
        self.pixel_scale = 30

        self.clock = pygame.time.Clock()
        self.frames = 0
        self.reset()

    def close(self):
        if self.renderOn:
            pygame.event.pump()
            pygame.display.quit()
            pygame.quit()

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
        self.pursuers_gone.fill(False)
        self.evaders_gone.fill(False)
        if self.random_opponents:
            if self.train_pursuit:
                self.n_evaders = self.np_random.randint(1, self.max_opponents)
            else:
                self.n_pursuers = self.np_random.randint(1, self.max_opponents)

        x_window_start = self.np_random.uniform(0.0, 1.0 - self.constraint_window)
        y_window_start = self.np_random.uniform(0.0, 1.0 - self.constraint_window)
        xlb, xub = int(self.xs * x_window_start), int(self.xs * (x_window_start + self.constraint_window))
        ylb, yub = int(self.ys * y_window_start), int(self.ys * (y_window_start + self.constraint_window))
        constraints = [[xlb, xub], [ylb, yub]]

        self.pursuers = agent_utils.create_agents(self.n_pursuers, self.map_matrix, self.obs_range, self.np_random,
                                                  randinit=True, constraints=constraints)
        self.pursuer_layer = AgentLayer(self.xs, self.ys, self.pursuers)

        self.evaders = agent_utils.create_agents(self.n_evaders, self.map_matrix, self.obs_range, self.np_random,
                                                 randinit=True, constraints=constraints)
        self.evader_layer = AgentLayer(self.xs, self.ys, self.evaders)

        self.latest_reward_state = [0 for _ in range(self.num_agents)]
        self.latest_done_state = [False for _ in range(self.num_agents)]
        self.latest_obs = [None for _ in range(self.num_agents)]

        self.model_state[0] = self.map_matrix
        self.model_state[1] = self.pursuer_layer.get_state_matrix()
        self.model_state[2] = self.evader_layer.get_state_matrix()

        self.frames = 0
        self.renderOn = False

        return self.safely_observe(0)

    def step(self, action, agent_id, is_last):
        if self.train_pursuit:
            agent_layer = self.pursuer_layer
            opponent_layer = self.evader_layer
            opponent_controller = self.evader_controller
        else:
            agent_layer = self.evader_layer
            opponent_layer = self.pursuer_layer
            opponent_controller = self.pursuer_controller

        if is_last:
            self.latest_reward_state = self.reward()

        # actual action application
        agent_layer.move_agent(agent_id, action)

        if is_last:
            ev_remove, pr_remove, pursuers_who_remove = self.remove_agents()

            for i in range(opponent_layer.n_agents()):
                # controller input should be an observation, but doesn't matter right now
                a = opponent_controller.act(self.model_state)
                opponent_layer.move_agent(i, a)

            self.latest_reward_state += self.term_pursuit * pursuers_who_remove
            self.latest_reward_state += self.urgency_reward

        self.model_state[0] = self.map_matrix
        self.model_state[1] = self.pursuer_layer.get_state_matrix()
        self.model_state[2] = self.evader_layer.get_state_matrix()

        if self.reward_mech == 'global' and is_last:
            meanVal = self.latest_reward_state.mean()
            self.latest_reward_state = [
                meanVal for _ in range(len(self.latest_reward_state))]

        if self.renderOn:
            self.clock.tick(15)
        else:
            self.clock.tick(2000)

        self.frames = self.frames + 1

    def draw_model_state(self):
        # -1 is building pixel flag
        x_len, y_len = self.model_state[0].shape
        for x in range(x_len):
            for y in range(y_len):
                pos = pygame.Rect(
                    self.pixel_scale * x, self.pixel_scale * y, self.pixel_scale, self.pixel_scale)
                col = (0, 0, 0)
                if self.model_state[0][x][y] == -1:
                    col = (255, 255, 255)
                pygame.draw.rect(self.screen, col, pos)

    def draw_pursuers_observations(self):
        for i in range(self.pursuer_layer.n_agents()):
            x, y = self.pursuer_layer.get_position(i)
            patch = pygame.Surface(
                (self.pixel_scale * self.obs_range, self.pixel_scale * self.obs_range))
            patch.set_alpha(128)
            patch.fill((255, 152, 72))
            ofst = self.obs_range / 2.0
            self.screen.blit(
                patch, (self.pixel_scale * (x - ofst + 1 / 2), self.pixel_scale * (y - ofst + 1 / 2)))

    def draw_pursuers(self):
        for i in range(self.pursuer_layer.n_agents()):
            x, y = self.pursuer_layer.get_position(i)
            center = (int(self.pixel_scale * x + self.pixel_scale / 2),
                      int(self.pixel_scale * y + self.pixel_scale / 2))
            col = (255, 0, 0)
            pygame.draw.circle(self.screen, col, center, int(self.pixel_scale / 3))

    def draw_evaders_observations(self):
        for i in range(self.evader_layer.n_agents()):
            x, y = self.evader_layer.get_position(i)
            patch = pygame.Surface(
                (self.pixel_scale * self.obs_range, self.pixel_scale * self.obs_range))
            patch.set_alpha(128)
            patch.fill((0, 154, 205))
            ofst = self.obs_range / 2.0
            self.screen.blit(
                patch, (self.pixel_scale * (x - ofst), self.pixel_scale * (y - ofst)))

    def draw_evaders(self):
        for i in range(self.evader_layer.n_agents()):
            x, y = self.evader_layer.get_position(i)
            center = (int(self.pixel_scale * x + self.pixel_scale / 2),
                      int(self.pixel_scale * y + self.pixel_scale / 2))
            col = (0, 0, 255)

            pygame.draw.circle(self.screen, col, center, int(self.pixel_scale / 3))

    def render(self):
        if not self.renderOn:
            pygame.display.init()
            self.screen = pygame.display.set_mode(
                (self.pixel_scale * self.xs, self.pixel_scale * self.ys))
        self.renderOn = True
        self.draw_model_state()
        if self.train_pursuit:
            self.draw_pursuers_observations()
        else:
            self.draw_evaders_observations()
        self.draw_evaders()
        self.draw_pursuers()

        pygame.display.flip()

    def animate(self, act_fn, nsteps, file_name, rate=1.5, verbose=False):
        """
            Save an animation to an mp4 file.
        """
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
            if done:
                break
        # use ffmpeg to create .pngs to .mp4 movie
        ffmpeg_cmd = "ffmpeg -framerate " + str(rate) + " -i " + join(
            file_path, "temp_%d.png") + " -c:v libx264 -pix_fmt yuv420p " + file_name
        call(ffmpeg_cmd.split())
        # clean-up by removing .pngs
        map(os.remove, glob.glob(join(file_path, "temp_*.png")))

    def save_image(self, file_name):
        self.render()
        capture = pygame.surfarray.array3d(self.screen)

        xl, xh = -self.obs_offset - 1, self.xs + self.obs_offset + 1
        yl, yh = -self.obs_offset - 1, self.ys + self.obs_offset + 1

        window = pygame.Rect(xl, yl, xh, yh)
        subcapture = capture.subsurface(window)

        pygame.image.save(subcapture, file_name)

    def reward(self):
        es = self.evader_layer.get_state_matrix()  # evader positions
        rewards = [
            self.catchr * np.sum(es[np.clip(
                self.pursuer_layer.get_position(
                    i)[0] + self.surround_mask[:, 0], 0, self.xs - 1
            ), np.clip(
                self.pursuer_layer.get_position(i)[1] + self.surround_mask[:, 1], 0, self.ys - 1)])
            for i in range(self.n_pursuers)
        ]
        return np.array(rewards)

    @property
    def is_terminal(self):
        # ev = self.evader_layer.get_state_matrix()  # evader positions
        # if np.sum(ev) == 0.0:
        if self.evader_layer.n_agents() == 0:
            return True
        return False

    def update_ally_controller(self, controller):
        self.ally_controller = controller

    def update_opponent_controller(self, controller):
        self.opponent_controller = controller

    def n_agents(self):
        return self.pursuer_layer.n_agents()

    def safely_observe(self, i):
        if self.train_pursuit:
            agent_layer = self.pursuer_layer
        else:
            agent_layer = self.evader_layer
        obs = self.collect_obs(agent_layer, i)
        return obs

    def collect_obs(self, agent_layer, i):
        if self.train_pursuit:
            gone_flags = self.pursuers_gone
        else:
            gone_flags = self.evaders_gone
        nage = 0
        for i in range(self.n_agents()):
            if not gone_flags[i]:
                if nage == i:
                    return self.collect_obs_by_idx(agent_layer, nage)
                nage += 1
        assert False, "bad index"

    def collect_obs_by_idx(self, agent_layer, agent_idx):
        # returns a flattened array of all the observations
        obs = np.zeros((3, self.obs_range, self.obs_range), dtype=np.float32)
        obs[0].fill(1.0)  # border walls set to -0.1?
        xp, yp = agent_layer.get_position(agent_idx)

        xlo, xhi, ylo, yhi, xolo, xohi, yolo, yohi = self.obs_clip(xp, yp)

        obs[0:3, xolo:xohi, yolo:yohi] = np.abs(self.model_state[0:3, xlo:xhi, ylo:yhi])
        return obs

    def obs_clip(self, x, y):
        xld = x - self.obs_offset
        xhd = x + self.obs_offset
        yld = y - self.obs_offset
        yhd = y + self.obs_offset
        xlo, xhi, ylo, yhi = (np.clip(xld, 0, self.xs - 1), np.clip(xhd, 0, self.xs - 1),
                              np.clip(yld, 0, self.ys - 1), np.clip(yhd, 0, self.ys - 1))
        xolo, yolo = abs(np.clip(xld, -self.obs_offset, 0)
                         ), abs(np.clip(yld, -self.obs_offset, 0))
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
                pos_that_catch = self.surround_mask + \
                    self.evader_layer.get_position(ai)
                truths = np.array(
                    [np.equal([xi, yi], pos_that_catch).all(axis=1) for xi, yi in zip(xpur, ypur)])
                if np.sum(truths.any(axis=0)) == self.need_to_surround(x, y):
                    removed_evade.append(ai - rems)
                    self.evaders_gone[i] = True
                    rems += 1
                    tt = truths.any(axis=1)
                    for j in range(self.n_pursuers):
                        xpp, ypp = self.pursuer_layer.get_position(j)
                        tes = np.concatenate(
                            (xpur[tt], ypur[tt])).reshape(2, len(xpur[tt]))
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
