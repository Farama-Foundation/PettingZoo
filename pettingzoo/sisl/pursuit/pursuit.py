from .pursuit_base import Pursuit as _env
from .manual_control import manual_control
from pettingzoo import AECEnv
from pettingzoo.utils import agent_selector
import numpy as np
from pettingzoo.utils import EnvLogger
import pygame


class env(AECEnv):

    metadata = {'render.modes': ['human']}

    def __init__(self, seed=None, *args, **kwargs):
        super(env, self).__init__()
        self.env = _env(*args, seed, **kwargs)
        pygame.init()
        self.num_agents = self.env.num_agents
        self.agents = ["pursuer_" + str(a) for a in range(self.num_agents)]
        self.agent_name_mapping = dict(zip(self.agents, list(range(self.num_agents))))
        self.agent_order = self.agents[:]
        self._agent_selector = agent_selector(self.agent_order)
        self.has_reset = False
        # spaces
        self.n_act_agents = self.env.act_dims[0]
        self.action_spaces = dict(zip(self.agents, self.env.action_space))
        self.observation_spaces = dict(
            zip(self.agents, self.env.observation_space))
        self.steps = 0
        self.display_wait = 0.0
        self.closed = False

    def reset(self, observe=True):
        self.has_reset = True
        self.steps = 0
        self.rewards = dict(
            zip(self.agents, [np.float64(0) for _ in self.agents]))
        self.dones = dict(zip(self.agents, [False for _ in self.agents]))
        self.infos = dict(zip(self.agents, [{} for _ in self.agents]))
        self._agent_selector.reinit(self.agent_order)
        self.agent_selection = self._agent_selector.next()
        self.env.reset()
        if observe:
            return self.observe(self.agent_selection)

    def close(self):
        if not self.has_reset:
            EnvLogger.warn_close_before_reset()
        elif not self.closed and self.has_reset:
            self.closed = True
            self.env.close()

    def render(self, mode="human"):
        if not self.has_reset:
            EnvLogger.error_render_before_reset()
        elif not self.closed:
            self.env.render()

    def step(self, action, observe=True):
        if not self.has_reset:
            EnvLogger.error_step_before_reset()
        agent = self.agent_selection
        if action is None or np.isnan(action):
            action = 0
            EnvLogger.warn_action_is_NaN(backup_policy="setting action to 0")
        elif not self.action_spaces[agent].contains(action):
            EnvLogger.warn_action_out_of_bound(action=action, action_space=self.action_spaces[agent], backup_policy="setting action to 0")
            action = 0
        self.env.step(action, self.agent_name_mapping[agent], self._agent_selector.is_last())
        for k in self.dones:
            if self.env.frames >= self.env.max_frames:
                self.dones[k] = True
            else:
                self.dones[k] = self.env.is_terminal
        for k in self.agents:
            self.rewards[k] = self.env.latest_reward_state[self.agent_name_mapping[k]]
        self.steps += 1
        self.agent_selection = self._agent_selector.next()
        if observe:
            return self.observe(self.agent_selection)

    def observe(self, agent):
        if not self.has_reset:
            EnvLogger.error_observe_before_reset()
        o = np.array(self.env.safely_observe(self.agent_name_mapping[agent]))
        return o
