import functools

import numpy as np
import pytest
from gymnasium import spaces

from pettingzoo import ParallelEnv
from pettingzoo.test.parallel_test import parallel_api_test


class PredictableDiscrete(spaces.Discrete):
    def sample(self, mask=None, probability=None):
        if mask is None:
            return 0
        return super().sample(mask=mask, probability=probability)


class ActionMaskParallelEnv(ParallelEnv):
    metadata = {"name": "action_mask_parallel_test_v0"}

    def __init__(self, mask_location):
        self.mask_location = mask_location
        self.possible_agents = ["player_0"]
        self.agents = []
        self.steps = 0
        self.max_cycles = 1
        self._action_space = PredictableDiscrete(3)

    @functools.cache
    def observation_space(self, agent):
        observation = spaces.Box(low=0, high=1, shape=(1,), dtype=np.int8)
        if self.mask_location in ("observation", "both"):
            return spaces.Dict(
                {
                    "observation": observation,
                    "action_mask": spaces.MultiBinary(3),
                }
            )
        return observation

    @functools.cache
    def action_space(self, agent):
        return self._action_space

    def _observations(self):
        observation = np.array([0], dtype=np.int8)
        if self.mask_location in ("observation", "both"):
            observation = {
                "observation": observation,
                "action_mask": np.array([0, 1, 0], dtype=np.int8),
            }
        return dict.fromkeys(self.agents, observation)

    def _infos(self):
        info = {}
        if self.mask_location in ("info", "both"):
            info["action_mask"] = np.array([0, 0, 1], dtype=np.int8)
        return {agent: info.copy() for agent in self.agents}

    def reset(self, seed=None, options=None):
        self.agents = list(self.possible_agents)
        self.steps = 0
        return self._observations(), self._infos()

    def step(self, actions):
        action = actions["player_0"]
        expected_action = {
            "info": 2,
            "observation": 1,
            "both": 1,
            "none": None,
        }[self.mask_location]
        if expected_action is not None:
            assert action == expected_action
        else:
            assert self.action_space("player_0").contains(action)

        self.steps += 1
        truncated = self.steps >= self.max_cycles
        agents = list(self.agents)
        observations = self._observations()
        infos = self._infos()
        rewards = dict.fromkeys(agents, 0.0)
        terminations = dict.fromkeys(agents, False)
        truncations = dict.fromkeys(agents, truncated)
        if truncated:
            self.agents = []
        return observations, rewards, terminations, truncations, infos


@pytest.mark.parametrize("mask_location", ["info", "observation", "both", "none"])
def test_parallel_api_test_samples_only_masked_actions(mask_location):
    parallel_api_test(ActionMaskParallelEnv(mask_location), num_cycles=3)
