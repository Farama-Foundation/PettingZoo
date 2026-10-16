from __future__ import annotations

import numpy as np
import pytest
from gymnasium.spaces import Box, Discrete

from pettingzoo.test import api_test
from pettingzoo.test.api_test import test_action_flexibility as check_action_flexibility
from pettingzoo.test.example_envs import (
    generated_agents_env_action_mask_info_v0,
    generated_agents_env_action_mask_obs_v0,
    generated_agents_env_v0,
)
from pettingzoo.utils.wrappers import AssertOutOfBoundsWrapper


class ActionSpaceEnv(generated_agents_env_v0.raw_env):
    def __init__(self, space):
        self.space = space
        self.actions = []
        self.reset_seeds = []
        super().__init__()

    def action_space(self, agent):
        return self.space

    def reset(self, seed=None, options=None):
        self.reset_seeds.append(seed)
        super().reset(seed=seed, options=options)

    def step(self, action):
        self.actions.append(action.copy() if isinstance(action, np.ndarray) else action)
        super().step(action)


@pytest.mark.parametrize("start", [0, 2, -5])
def test_discrete_action_flexibility(start):
    env = ActionSpaceEnv(Discrete(3, start=start))
    check_action_flexibility(AssertOutOfBoundsWrapper(env))
    assert env.reset_seeds == [0, 0]
    assert len(env.actions) == 2
    assert type(env.actions[0]) is int
    assert type(env.actions[1]) is np.int32
    assert env.actions[0] == env.actions[1] == start


@pytest.mark.parametrize("dtype", [np.float32, np.float64, np.int32])
@pytest.mark.parametrize("bounds", [(-1, 1), (1, 2), (-3, -1)])
@pytest.mark.parametrize("shape", [(), (2,)])
def test_box_action_flexibility(dtype, bounds, shape):
    env = ActionSpaceEnv(Box(*bounds, shape=shape, dtype=dtype))
    check_action_flexibility(AssertOutOfBoundsWrapper(env))
    assert env.reset_seeds == [0, 0]
    assert len(env.actions) == 2
    np.testing.assert_array_equal(env.actions[0], env.actions[1])
    assert all(isinstance(action, np.ndarray) for action in env.actions)
    assert all(action.dtype == dtype for action in env.actions)


def test_box_action_flexibility_preserves_action_across_resets():
    class MutatingActionEnv(ActionSpaceEnv):
        def step(self, action):
            super().step(action)
            action[:] = -99

    env = MutatingActionEnv(Box(np.array([1, -3]), np.array([2, -1]), dtype=np.float64))
    check_action_flexibility(AssertOutOfBoundsWrapper(env))
    np.testing.assert_array_equal(env.actions[0], env.actions[1])
    assert all(env.space.contains(action) for action in env.actions)


@pytest.mark.parametrize(
    "env_constructor",
    [
        generated_agents_env_action_mask_obs_v0.env,
        generated_agents_env_action_mask_info_v0.env,
    ],
)
def test_action_flexibility_preserves_masks(env_constructor):
    check_action_flexibility(env_constructor())


@pytest.mark.parametrize(
    "space", [Discrete(3, start=2), Box(1, 2, shape=(2,), dtype=np.float32)]
)
def test_api_accepts_action_spaces_without_zero(space):
    api_test(AssertOutOfBoundsWrapper(ActionSpaceEnv(space)), num_cycles=10)
