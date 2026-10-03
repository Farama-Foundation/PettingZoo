"""Tests that the environment's state() and state_space() methods work as expected."""

from __future__ import annotations

import warnings
from typing import Any

import gymnasium
import numpy as np

from pettingzoo.test.parallel_test import sample_action
from pettingzoo.utils.env import AECEnv, ParallelEnv
from pettingzoo.utils.wrappers.base import BaseWrapper
from pettingzoo.utils.wrappers.base_parallel import BaseParallelWrapper

try:
    """Allows doctests to be run using pytest"""
    import pytest

    from pettingzoo.test.example_envs import (
        generated_agents_env_v0,
        generated_agents_parallel_v0,
    )

    @pytest.fixture
    def env():
        return generated_agents_env_v0.env()

    @pytest.fixture
    def parallel_env():
        return generated_agents_parallel_v0.parallel_env()

    @pytest.fixture
    def num_cycles():
        return 1000

except ModuleNotFoundError:
    pass


env_pos_inf_state = [
    "simple_adversary_v3",
    "simple_reference_v3",
    "simple_spread_v3",
    "simple_tag_v3",
    "simple_world_comm_v3",
    "simple_crypto_v3",
    "simple_push_v3",
    "simple_speaker_listener_v4",
    "simple_v3",
]
env_neg_inf_state = [
    "simple_adversary_v3",
    "simple_reference_v3",
    "simple_spread_v3",
    "simple_tag_v3",
    "simple_world_comm_v3",
    "simple_crypto_v3",
    "simple_push_v3",
    "simple_speaker_listener_v4",
    "simple_v3",
]
graphical_envs = ["knights_archers_zombies_v11"]


def test_state_space(env):
    assert isinstance(env.state_space, gymnasium.spaces.Space), (
        "State space for each environment must extend gymnasium.spaces.Space"
    )

    if isinstance(env.state_space, gymnasium.spaces.Box):
        if (
            np.any(np.equal(env.state_space.low, -np.inf))
            and str(env.unwrapped) not in env_neg_inf_state
        ):
            warnings.warn(
                "Environment's minimum state space value is -infinity. "
                "This is probably too low."
            )
        if (
            np.any(np.equal(env.state_space.high, np.inf))
            and str(env.unwrapped) not in env_pos_inf_state
        ):
            warnings.warn(
                "Environment's maximum state space value is infinity. "
                "This is probably too high"
            )
        if np.any(np.equal(env.state_space.low, env.state_space.high)):
            warnings.warn(
                "Environment's maximum and minimum state space values are equal"
            )
        if np.any(np.greater(env.state_space.low, env.state_space.high)):
            raise AssertionError(
                "Environment's minimum state space value is greater than it's maximum"
            )
        if env.state_space.low.shape != env.state_space.shape:
            raise AssertionError(
                "Environment's state_space.low and state_space have different shapes"
            )
        if env.state_space.high.shape != env.state_space.shape:
            raise AssertionError(
                "Environment's state_space.high and state_space have different shapes"
            )


def _check_state(env, new_state: Any, state_0: Any) -> None:
    assert env.state_space.contains(new_state), (
        "Environment's state is outside of it's state space"
    )

    if not isinstance(new_state, state_0.__class__):
        warnings.warn("States are different classes")

    if not isinstance(new_state, np.ndarray):
        return

    if np.isinf(new_state).any():
        warnings.warn(
            "State contains infinity (np.inf) or negative infinity (-np.inf)"
        )
    if np.isnan(new_state).any():
        warnings.warn("State contains NaNs")
    if len(new_state.shape) > 3:
        warnings.warn("State has more than 3 dimensions")
    if new_state.shape == (0,):
        raise AssertionError("State can not be an empty array")
    if new_state.shape == (1,):
        warnings.warn("State is a single number")
    if isinstance(state_0, np.ndarray):
        if (new_state.shape != state_0.shape) and (
            len(new_state.shape) == len(state_0.shape)
        ):
            warnings.warn("States are different shapes")
        if len(new_state.shape) != len(state_0.shape):
            warnings.warn("States have different number of dimensions")
    if not np.can_cast(new_state.dtype, np.dtype("float64")):
        warnings.warn("State numpy array is not a numeric dtype")
    if np.array_equal(new_state, np.zeros(new_state.shape)):
        warnings.warn("State numpy array is all zeros.")
    if (
        not np.all(new_state >= 0)
        and (
            (len(new_state.shape) == 2)
            or (len(new_state.shape) == 3 and new_state.shape[2] == 1)
            or (len(new_state.shape) == 3 and new_state.shape[2] == 3)
        )
        and str(env.unwrapped) not in graphical_envs
    ):
        warnings.warn(
            "The state contains negative numbers and is in the shape of a graphical "
            "observation. This might be a bad thing."
        )


def test_state(env: AECEnv, num_cycles: int, seed: int | None = 0):
    env.reset(seed=seed)
    state_0 = env.state()
    _check_state(env, state_0, state_0)

    for agent in env.agent_iter(env.num_agents * num_cycles):
        _, _, terminated, truncated, _ = env.last(observe=False)
        if terminated or truncated:
            action = None
        else:
            action = env.action_space(agent).sample()

        env.step(action)
        _check_state(env, env.state(), state_0)


def test_parallel_env(
    parallel_env: ParallelEnv, num_cycles: int = 10, seed: int | None = 0
):
    observations, _ = parallel_env.reset(seed=seed)

    assert isinstance(parallel_env.state_space, gymnasium.spaces.Space), (
        "State space for each parallel environment must extend gymnasium.spaces.Space"
    )

    state_0 = parallel_env.state()
    _check_state(parallel_env, state_0, state_0)

    for _ in range(num_cycles):
        if not parallel_env.agents:
            break
        actions = {
            agent: sample_action(parallel_env, observations, agent)
            for agent in parallel_env.agents
        }
        observations, _, _, _, _ = parallel_env.step(actions)
        _check_state(parallel_env, parallel_env.state(), state_0)


class _DictStateAEC(BaseWrapper):
    def __init__(self, env: AECEnv):
        super().__init__(env)
        self.state_space = gymnasium.spaces.Dict({"base": env.state_space})

    def state(self) -> dict[str, Any]:
        return {"base": self.env.state()}


class _DictStateParallel(BaseParallelWrapper):
    def __init__(self, env: ParallelEnv):
        super().__init__(env)
        self.state_space = gymnasium.spaces.Dict({"base": env.state_space})

    def state(self) -> dict[str, Any]:
        return {"base": self.env.state()}


def test_dict_state_space(env, parallel_env):
    state_test(_DictStateAEC(env), _DictStateParallel(parallel_env), num_cycles=3)


def state_test(env, parallel_env, num_cycles=10):
    test_state_space(env)
    test_state(env, num_cycles)
    test_parallel_env(parallel_env, num_cycles)
