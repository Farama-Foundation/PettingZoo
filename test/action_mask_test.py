import gymnasium
import numpy as np
import pytest

from pettingzoo.test import seed_test
from pettingzoo.test.example_envs import (
    generated_agents_env_action_mask_info_v0,
    generated_agents_env_action_mask_obs_v0,
)
from pettingzoo.test.parallel_test import parallel_api_test
from pettingzoo.utils.env import AECEnv, ParallelEnv


@pytest.mark.parametrize(
    "env_constructor",
    [
        generated_agents_env_action_mask_info_v0.env,
        generated_agents_env_action_mask_obs_v0.env,
    ],
)
def test_action_mask(env_constructor: type[AECEnv]):
    """Test that environments function deterministically in cases where action mask is in observation, or in info."""
    seed_test(env_constructor)

    # Step through the environment according to example code given in AEC documentation (following action mask)
    env = env_constructor()
    env.reset(seed=42)
    for agent in env.agent_iter():
        observation, reward, termination, truncation, info = env.last()

        if termination or truncation:
            action = None
        else:
            # invalid action masking is optional and environment-dependent
            if "action_mask" in info:
                mask = info["action_mask"]
            elif isinstance(observation, dict) and "action_mask" in observation:
                mask = observation["action_mask"]
            else:
                mask = None
            action = env.action_space(agent).sample(mask)
        env.step(action)
    env.close()


class DeterministicDiscrete(gymnasium.spaces.Discrete):
    def sample(self, mask=None, probability=None):
        if mask is None:
            return 0
        return super().sample(mask=mask, probability=probability)


class ActionMaskParallelEnv(ParallelEnv[str, np.ndarray | dict[str, np.ndarray], int]):
    metadata = {"name": "action_mask_parallel"}

    def __init__(self, info_mask=None, observation_mask=None):
        self.possible_agents = ["agent_0"]
        self.agents = []
        self.max_cycles = 3
        self.steps = 0
        self.info_mask = info_mask
        self.observation_mask = observation_mask
        self.valid_mask = info_mask if info_mask is not None else observation_mask
        self._action_space = DeterministicDiscrete(3)
        self._array_space = gymnasium.spaces.Box(
            low=0, high=1, shape=(1,), dtype=np.int8
        )
        if observation_mask is None:
            self._observation_space = self._array_space
        else:
            self._observation_space = gymnasium.spaces.Dict(
                {
                    "observation": self._array_space,
                    "action_mask": gymnasium.spaces.Box(
                        low=0, high=1, shape=(3,), dtype=np.int8
                    ),
                }
            )

    def action_space(self, agent):
        return self._action_space

    def observation_space(self, agent):
        return self._observation_space

    def _observation(self):
        observation = np.array([0], dtype=np.int8)
        if self.observation_mask is None:
            return observation
        return {
            "observation": observation,
            "action_mask": self.observation_mask,
        }

    def _infos(self):
        if self.info_mask is None:
            return {"agent_0": {}}
        return {"agent_0": {"action_mask": self.info_mask}}

    def reset(self, seed=None, options=None):
        self.agents = self.possible_agents.copy()
        self.steps = 0
        return {"agent_0": self._observation()}, self._infos()

    def step(self, actions):
        action = actions["agent_0"]
        if self.valid_mask is not None:
            assert self.valid_mask[action], (
                "parallel_api_test sampled an invalid action"
            )

        self.steps += 1
        truncated = self.steps >= self.max_cycles
        if truncated:
            self.agents = []
        return (
            {"agent_0": self._observation()},
            {"agent_0": 0.0},
            {"agent_0": False},
            {"agent_0": truncated},
            self._infos(),
        )


@pytest.mark.parametrize(
    ("info_mask", "observation_mask"),
    [
        (np.array([0, 1, 0], dtype=np.int8), None),
        (None, np.array([0, 0, 1], dtype=np.int8)),
        (
            np.array([0, 1, 0], dtype=np.int8),
            np.array([0, 0, 1], dtype=np.int8),
        ),
        (None, None),
    ],
)
def test_parallel_api_action_mask(info_mask, observation_mask):
    parallel_api_test(ActionMaskParallelEnv(info_mask, observation_mask), num_cycles=3)
