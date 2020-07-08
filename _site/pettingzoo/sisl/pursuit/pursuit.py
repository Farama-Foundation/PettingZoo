from .pursuit_base import Pursuit as _env
from .manual_control import manual_control
from pettingzoo import AECEnv
from pettingzoo.utils import agent_selector
import numpy as np
import pygame
from pettingzoo.utils import wrappers


def env(**kwargs):
    env = raw_env(**kwargs)
    example_space = list(env.action_spaces.values())[0]
    env = wrappers.AssertOutOfBoundsWrapper(env)
    env = wrappers.NanNoOpWrapper(env, np.zeros(example_space.shape, dtype=example_space.dtype), "taking all zeros action")
    env = wrappers.OrderEnforcingWrapper(env)
    return env


class raw_env(AECEnv):

    metadata = {'render.modes': ['human']}

    def __init__(self, seed=None, *args, **kwargs):
        super().__init__()
        self.env = _env(*args, seed, **kwargs)
        pygame.init()
        self.num_agents = self.env.num_agents
        self.agents = ["pursuer_" + str(a) for a in range(self.num_agents)]
        self.agent_name_mapping = dict(zip(self.agents, list(range(self.num_agents))))
        self._agent_selector = agent_selector(self.agents)
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
        self._agent_selector.reinit(self.agents)
        self.agent_selection = self._agent_selector.next()
        self.env.reset()
        if observe:
            return self.observe(self.agent_selection)

    def close(self):
        if not self.closed and self.has_reset:
            self.closed = True
            self.env.close()

    def render(self, mode="human"):
        if not self.closed:
            self.env.render()

    def step(self, action, observe=True):
        agent = self.agent_selection
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
        o = np.array(self.env.safely_observe(self.agent_name_mapping[agent]), np.float32)
        return o
