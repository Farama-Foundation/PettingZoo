from gym import spaces
import numpy as np
from pettingzoo import AECEnv
from pettingzoo.utils.agent_selector import agent_selector
from pettingzoo.utils.env_logger import EnvLogger
from gym.utils import seeding


class SimpleEnv(AECEnv):

    metadata = {'render.modes': ['human']}

    def __init__(self, scenario, world, max_frames, seed, global_reward_weight=None):
        super(SimpleEnv, self).__init__()

        self.np_random, seed = seeding.np_random(seed)

        self.max_frames = max_frames
        self.scenario = scenario
        self.world = world
        self.global_reward_weight = global_reward_weight

        self.scenario.reset_world(self.world, self.np_random)

        self.num_agents = len(self.world.agents)
        self.agents = [agent.name for agent in self.world.agents]
        self._index_map = {agent.name: idx for idx, agent in enumerate(self.world.agents)}

        self.agent_order = list(self.agents)

        self._agent_selector = agent_selector(self.agent_order)

        # set spaces
        self.action_spaces = dict()
        self.observation_spaces = dict()
        for agent in self.world.agents:
            space_dim = 1
            if agent.movable:
                space_dim *= self.world.dim_p * 2 + 1
            if not agent.silent:
                space_dim *= self.world.dim_c

            obs_dim = len(self.scenario.observation(agent, self.world))
            self.action_spaces[agent.name] = spaces.Discrete(space_dim)
            self.observation_spaces[agent.name] = spaces.Box(low=-np.inf, high=+np.inf, shape=(obs_dim,), dtype=np.float32)

        self.steps = 0

        self.current_actions = [None] * self.num_agents

        self.viewer = None

        self.has_reset = False

    def observe(self, agent):
        assert self.has_reset, EnvLogger.error_observe_before_reset()
        return self.scenario.observation(self.world.agents[self._index_map[agent]], self.world)

    def reset(self, observe=True):
        self.has_reset = True

        self.scenario.reset_world(self.world, self.np_random)

        self.rewards = {name: 0. for name in self.agents}
        self.dones = {name: False for name in self.agents}
        self.infos = {name: {} for name in self.agents}

        self._reset_render()

        self.agent_selection = self._agent_selector.reset()
        self.steps = 0

        self.current_actions = [None] * self.num_agents

        if observe:
            agent = self.world.agents[0]
            return self.scenario.observation(agent, self.world)
        else:
            return

    def _execute_world_step(self):
        self.steps += 1
        # set action for each agent
        for i, agent in enumerate(self.world.agents):
            action = self.current_actions[i]
            scenario_action = []
            if agent.movable:
                mdim = self.world.dim_p * 2 + 1
                scenario_action.append(action % mdim)
                action //= mdim
            if not agent.silent:
                scenario_action.append(action)

            self._set_action(scenario_action, agent, self.action_spaces[agent.name])

        self.world.step()

        global_reward = 0.
        if self.global_reward_weight is not None:
            global_reward = float(self.scenario.global_reward(self.world))

        for agent in self.world.agents:
            agent_reward = float(self.scenario.reward(agent, self.world))
            if self.global_reward_weight is not None:
                reward = global_reward * self.global_reward_weight + agent_reward * (1. - self.global_reward_weight)
            else:
                reward = agent_reward

            self.rewards[agent.name] = reward

    # set env action for a particular agent
    def _set_action(self, action, agent, action_space, time=None):
        agent.action.u = np.zeros(self.world.dim_p)
        agent.action.c = np.zeros(self.world.dim_c)
        # process action

        if agent.movable:
            # physical action
            agent.action.u = np.zeros(self.world.dim_p)
            # process discrete action
            if action[0] == 1:
                agent.action.u[0] = -1.0
            if action[0] == 2:
                agent.action.u[0] = +1.0
            if action[0] == 3:
                agent.action.u[1] = -1.0
            if action[0] == 4:
                agent.action.u[1] = +1.

            sensitivity = 5.0
            if agent.accel is not None:
                sensitivity = agent.accel
            agent.action.u *= sensitivity
            action = action[1:]
        if not agent.silent:
            # communication action
            agent.action.c = np.zeros(self.world.dim_c)

            agent.action.c[action[0]] = 1.0
            action = action[1:]
        # make sure we used all elements of action
        assert len(action) == 0

    def step(self, action, observe=True):
        if not self.has_reset:
            EnvLogger.error_step_before_reset()
        backup_policy = "taking zero action (no movement, communication 0)"
        act_space = self.action_spaces[self.agent_selection]
        if np.isnan(action).any():
            EnvLogger.warn_action_is_NaN(backup_policy)
        if not act_space.contains(action):
            EnvLogger.warn_action_out_of_bound(action, act_space, backup_policy)

        current_idx = self._index_map[self.agent_selection]
        next_idx = (current_idx + 1) % self.num_agents
        self.agent_selection = self._agent_selector.next()

        self.current_actions[current_idx] = action

        if next_idx == 0:
            self._execute_world_step()
            if self.steps > self.max_frames:
                for a in self.agents:
                    self.dones[a] = True

        next_agent = self.world.agents[next_idx]
        if observe:
            next_observation = self.scenario.observation(next_agent, self.world)
        else:
            next_observation = None
        return next_observation

    def render(self, mode='human'):
        from . import rendering

        if self.viewer is None:
            self.viewer = rendering.Viewer(700, 700)

        # create rendering geometry
        if self.render_geoms is None:
            # import rendering only if we need it (and don't import for headless machines)
            # from gym.envs.classic_control import rendering
            # from multiagent._mpe_utils import rendering
            self.render_geoms = []
            self.render_geoms_xform = []
            for entity in self.world.entities:
                geom = rendering.make_circle(entity.size)
                xform = rendering.Transform()
                if 'agent' in entity.name:
                    geom.set_color(*entity.color[:3], alpha=0.5)
                else:
                    geom.set_color(*entity.color[:3])
                geom.add_attr(xform)
                self.render_geoms.append(geom)
                self.render_geoms_xform.append(xform)

            # add geoms to viewer
            self.viewer.geoms = []
            for geom in self.render_geoms:
                self.viewer.add_geom(geom)

            self.viewer.text_lines = []
            idx = 0
            for agent in self.world.agents:
                if not agent.silent:
                    tline = rendering.TextLine(self.viewer.window, idx)
                    self.viewer.text_lines.append(tline)
                    idx += 1

        alphabet = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
        # for agent in self.world.agents:
        idx = 0
        for idx, other in enumerate(self.world.agents):
            if other.silent:
                continue
            if np.all(other.state.c == 0):
                word = '_'
            else:
                word = alphabet[np.argmax(other.state.c)]

            message = (other.name + ' sends ' + word + '   ')

            self.viewer.text_lines[idx].set_text(message)
            idx += 1

        # update bounds to center around agent
        all_poses = [entity.state.p_pos for entity in self.world.entities]
        cam_range = np.max(np.abs(np.array(all_poses))) + 1
        self.viewer.set_max_size(cam_range)
        # update geometry positions
        for e, entity in enumerate(self.world.entities):
            self.render_geoms_xform[e].set_translation(*entity.state.p_pos)
        # render to display or array
        return self.viewer.render(return_rgb_array=mode == 'rgb_array')

    # reset rendering assets
    def _reset_render(self):
        self.render_geoms = None
        self.render_geoms_xform = None

    def close(self):
        if self.viewer is not None:
            self.viewer.close()
            self.viewer = None
        else:
            EnvLogger.warn_close_unrendered_env()
        self._reset_render()
