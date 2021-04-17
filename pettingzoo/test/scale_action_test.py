from gym.spaces import Box, Discrete
import numpy as np
from supersuit import (
    scale_actions_wrapper
)
import supersuit
import pytest
from pettingzoo.utils.wrappers import OrderEnforcingWrapper as PettingzooWrap

base_obs = {"a{}".format(idx): np.zeros([8, 8, 3], dtype=np.float32) + np.arange(3) + idx for idx in range(2)}
base_obs_space = {"a{}".format(idx): Box(low=np.float32(0.0), high=np.float32(10.0), shape=[8, 8, 3]) for idx in range(2)}
base_act_spaces = {"a{}".format(idx): Discrete(5) for idx in range(2)}

class DummyEnv(AECEnv):
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
        return action

def test_scale_action_wrapper():
    base_env = DummyEnv(base_obs, base_obs_space, base_act_spaces)
    wrapped_env = scale_actions_wrapper(base_env, 2)
    scaled_action = wrapped_env.step(2)
    assert scaled_action == 4