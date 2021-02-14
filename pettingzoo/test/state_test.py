import pettingzoo
import warnings
import numpy as np
import gym
import random
import re


def test_state_space(env):
    assert isinstance(env.state_space, gym.spaces.Space), "State space for each environment must extend gym.spaces.Space"
    if not (isinstance(env.state_space, gym.spaces.Box) or isinstance(env.state_space, gym.spaces.Discrete)):
        warnings.warn("State space for each environment probably should be gym.spaces.box or gym.spaces.discrete")

    if isinstance(env.state_space, gym.spaces.Box):
        if np.any(np.equal(env.state_space.low, -np.inf)):
            warnings.warn("Environment's minimum state space value is -infinity. This is probably too low.")
        if np.any(np.equal(env.state_space.high, np.inf)):
            warnings.warn("Environment's maxmimum state space value is infinity. This is probably too high")
        if np.any(np.equal(env.state_space.low, env.state_space.high)):
            warnings.warn("Environment's maximum and minimum state space values are equal")
        if np.any(np.greater(env.state_space.low, env.state_space.high)):
            assert False, "Environment's minimum state space value is greater than it's maximum"
        if env.state_space.low.shape != env.state_space.shape:
            assert False, "Environment's state_space.low and state_space have different shapes"
        if env.state_space.high.shape != env.state_space.shape:
            assert False, "Environment's state_space.high and state_space have different shapes"


def test_state(env, num_cycles):
    env.reset()
    state_0 = env.state()
    for agent in env.agent_iter(env.num_agents * num_cycles):
        observation, reward, done, info = env.last(observe=False)
        if done:
            action = None
        else:
            action = env.action_spaces[agent].sample()

        env.step(action)
        new_state = env.state()
        assert env.state_space.contains(new_state), "Environment's state is outside of it's state space"
        if isinstance(new_state, np.ndarray):
            if np.isinf(new_state).any():
                warnings.warn("State contains infinity (np.inf) or negative infinity (-np.inf)")
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
            if (new_state.shape != state_0.shape) and (len(new_state.shape) == len(state_0.shape)):
                warnings.warn("States are different shapes")
            if len(new_state.shape) != len(state_0.shape):
                warnings.warn("States have different number of dimensions")
            if not np.can_cast(new_state.dtype, np.dtype("float64")):
                warnings.warn("State numpy array is not a numeric dtype")
            if np.array_equal(new_state, np.zeros(new_state.shape)):
                warnings.warn("State numpy array is all zeros.")
            if not np.all(new_state >= 0) and ((len(new_state.shape) == 2) or (len(new_state.shape) == 3 and new_state.shape[2] == 1) or (len(new_state.shape) == 3 and new_state.shape[2] == 3)):
                warnings.warn("The state contains negative numbers and is in the shape of a graphical observation. This might be a bad thing.")
        else:
            warnings.warn("State is not NumPy array")


def test_parallel_env(parallel_env):

    parallel_env.reset()

    assert isinstance(parallel_env.state_space, gym.spaces.Space), "State space for each parallel environment must extend gym.spaces.Space"

    state_0 = parallel_env.state()
    assert parallel_env.state_space.contains(state_0), "ParallelEnvironment's state is outside of it's state space"


def state_test(env, parallel_env, num_cycles=10):
    test_state_space(env)
    test_state(env, num_cycles)
    test_parallel_env(parallel_env)
