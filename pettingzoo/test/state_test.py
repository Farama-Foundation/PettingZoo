from __future__ import annotations

from pettingzoo.utils.env import AECEnv, ParallelEnv

"""Tests that the environment's state() and state_space() methods work as expected."""
import warnings

import gymnasium
import numpy as np

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


def test_state_space(env):
    assert isinstance(
        env.state_space, gymnasium.spaces.Space
    ), "State space for each environment must extend gymnasium.spaces.Space"
    if not (
        isinstance(env.state_space, gymnasium.spaces.Box)
        or isinstance(env.state_space, gymnasium.spaces.Discrete)
    ):
        warnings.warn(
            "State space for each environment probably should be gymnasium.spaces.box or gymnasium.spaces.discrete"
        )

    if isinstance(env.state_space, gymnasium.spaces.Box):
        if (
            np.any(np.equal(env.state_space.low, -np.inf))
            and str(env.unwrapped) not in env_neg_inf_state
        ):
            warnings.warn(
                "Environment's minimum state space value is -infinity. This is probably too low."
            )
        if (
            np.any(np.equal(env.state_space.high, np.inf))
            and str(env.unwrapped) not in env_pos_inf_state
        ):
            warnings.warn(
                "Environment's maximum state space value is infinity. This is probably too high"
            )
        if np.any(np.equal(env.state_space.low, env.state_space.high)):
            warnings.warn(
                "Environment's maximum and minimum state space values are equal"
            )
        if np.any(np.greater(env.state_space.low, env.state_space.high)):
            assert (
                False
            ), "Environment's minimum state space value is greater than it's maximum"
        if env.state_space.low.shape != env.state_space.shape:
            assert (
                False
            ), "Environment's state_space.low and state_space have different shapes"
        if env.state_space.high.shape != env.state_space.shape:
            assert (
                False
            ), "Environment's state_space.high and state_space have different shapes"


def test_state(env: AECEnv, num_cycles: int, seed: int | None = 0):
    graphical_envs = ["knights_archers_zombies_v10"]
    env.reset(seed=seed)
    state_0 = env.state()
    for agent in env.agent_iter(env.num_agents * num_cycles):
        observation, reward, terminated, truncated, info = env.last(observe=False)
        if terminated or truncated:
            action = None
        else:
            action = env.action_space(agent).sample()

        env.step(action)
        new_state = env.state()
        assert env.state_space.contains(
            new_state
        ), "Environment's state is outside of it's state space"
        if (
            not isinstance(new_state, np.ndarray)
            and str(env.unwrapped) not in graphical_envs
        ):
            warnings.warn("State is not NumPy array")
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
            assert False, "State can not be an empty array"
        if new_state.shape == (1,):
            warnings.warn("State is a single number")
        if not isinstance(new_state, state_0.__class__):
            warnings.warn("State between Observations are different classes")
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
                "The state contains negative numbers and is in the shape of a graphical observation. This might be a bad thing."
            )


def test_parallel_env(parallel_env: ParallelEnv, seed: int | None = 0):
    parallel_env.reset(seed=seed)

    assert isinstance(
        parallel_env.state_space, gymnasium.spaces.Space
    ), "State space for each parallel environment must extend gymnasium.spaces.Space"

    state_0 = parallel_env.state()
    assert parallel_env.state_space.contains(
        state_0
    ), "ParallelEnvironment's state is outside of it's state space"


def state_test(env, parallel_env, num_cycles=10):
    test_state_space(env)
    test_state(env, num_cycles)
    test_parallel_env(parallel_env)
