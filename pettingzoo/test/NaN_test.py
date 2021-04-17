from gym.spaces import Box, Discrete
import numpy as np
from pettingzoo import AECEnv
import copy
from pettingzoo.utils.agent_selector import agent_selector
import pytest
from pettingzoo.utils.wrappers import OrderEnforcingWrapper as PettingzooWrap

base_obs = {"a{}".format(idx): np.zeros([8, 8, 3], dtype=np.float32) + np.arange(3) + idx for idx in range(2)}
base_obs_space = {"a{}".format(idx): Box(low=np.float32(0.0), high=np.float32(10.0), shape=[8, 8, 3]) for idx in range(2)}
base_act_spaces = {"a{}".format(idx): Discrete(5) for idx in range(2)}

class DummyNaNEnv(AECEnv):
    metadata = {"render.modes": ["human"]}

    def __init__(self, observations, observation_spaces, action_spaces):
        super().__init__()
        self._observations = observations
        self.observation_spaces = observation_spaces

        self.agents = sorted([x for x in observation_spaces.keys()])
        self.possible_agents = self.agents[:]
        self._agent_selector = agent_selector(self.agents)
        self.agent_selection = self._agent_selector.reset()
        self.action_spaces = action_spaces

        self.steps = 0

    def step(self, action, observe=True):
        assert (not (np.isnan(action))), "Action was a NaN, even though it should not have been."

def test_NaN_noop_wrapper():
    base_env = DummyNaNEnv(base_obs, base_obs_space, base_act_spaces)
    wrapped_env = nan_noop_wrapper(base_env)
    wrapped_env.step(np.nan)

def test_NaN_zeros_wrapper():
    base_env = DummyEnv(base_obs, base_obs_space, base_act_spaces)
    wrapped_env = nan_zeros_wrapper(base_env)
    wrapped_env.step(np.nan)

def test_NaN_random_wrapper():
    base_env = DummyEnv(base_obs, base_obs_space, base_act_spaces)
    wrapped_env = nan_random_wrapper(base_env)
    wrapped_env.step(np.nan)


