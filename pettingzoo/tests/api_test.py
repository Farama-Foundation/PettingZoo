import pettingzoo
import warnings
import numpy as np
import gym


def test_obervation(observation, observation_0):
    if isinstance(observation, np.ndarray):
        if np.isinf(observation).any():
            warnings.warn("Observation contains infinity (np.inf) or negative infinity (-np.inf)")
        if np.isnan(observation).any():
            warnings.warn("Observation contains NaNs")
        if len(observation.shape) > 3:
            warnings.warn("Observation has more than 3 deminsions")
        if observation.shape == (0,):
            raise Exception("Observation is empty array")
        if observation.shape == (1,):
            warnings.warn("Observation is a single number")
        assert isinstance(observation, observation_0)
        if (observation.shape != observation_0.shape) and (len(observation.shape) == len(observation_0.shape)):
            warnings.warn("Observations are different shapes")
        if len(observation.shape) != len(observation_0.shape):
            warnings.warn("Observations have different number of deminsions")
        assert observation.dtype is np.dtype('f') or np.dtype('u') or np.dtype('i')
    else:
        warnings.warn("Observation is not NumPy array")


def mandatory_tests(env):
    assert isinstance(env, pettingzoo.AECEnv)

    observation = env.reset(observe=False)
    assert observation is None

    observation_0 = env.reset()
    test_obervation(observation_0, observation_0)

    assert isinstance(env.agent_order, list)
    assert isinstance(env.action_spaces, dict)
    assert isinstance(env.observation_spaces, dict)
    assert len(env.observation_spaces) == len(env.action_spaces) == len(env.agents)

    agent_0 = env.agent_order[0]

    for agent in env.agents:  # observation and action space loop
        assert isinstance(env.observation_spaces[agent], gym.spaces.box) or isinstance(env.observation_spaces[agent], gym.spaces.discrete)
        assert isinstance(env.action_spaces[agent], gym.spaces.box) or isinstance(env.action_spaces[agent], gym.spaces.discrete)
        if (not isinstance(agent, int)) and agent != 'env':
            warnings.warn("Agent's are recommended to have integer names")
        assert isinstance(env.observation_spaces[agent], env.observation_spaces[agent_0])
        assert isinstance(env.action_spaces[agent], env.action_spaces[agent_0])
        if env.observation_spaces[agent] != env.observation_spaces[agent_0]:
            warnings.warn("Agents have different observation space sizes")
        if env.action_spaces[agent] != env.action_spaces[agent_0]:
            warnings.warn("Agents have different observation space sizes")

    for agent in env.agent_order:  # step through every agent once with observe = True
        action = env.action_spaces[agent].sample()
        observation = env.step(action)
        assert env.observation_spaces[agent].contains(agent)
        test_obervation(observation, observation_0)

    for agent in env.agent_order:  # step through every agent once with observe = False
        action = env.action_spaces[agent].sample()
        observation = env.step(action, observe=False)
        assert observation is None

    assert isinstance(env.rewards, dict)
    assert isinstance(env.dones, dict)
    assert isinstance(env.infos, dict)

    assert len(env.rewards) == len(env.dones) == len(env.infos) == len(env.agents)

    for agent in env.agents:  # reward checking loop
        assert isinstance(env.dones[agent], bool)

        if not ((isinstance(env.rewards[agent], int) or isinstance(env.rewards[agent], float)) and not isinstance(env.rewards[agent], np.ndarray)):
            warnings.warn("Reward should be int, float, or numpy array")
        if isinstance(env.rewards[agent], np.ndarray):
            if isinstance(env.rewards[agent], np.ndarray) and not env.rewards[agent].shape == (1,):
                raise Exception("Rewards can only be one number")
            if np.isinf(env.rewards[agent]):
                raise Exception("Reward must be finite")
            if np.isnan(env.rewards[agent]):
                raise Exception("Rewards cannot be NaN")

        assert isinstance(env.rewards[agent], env.rewards[agent_0])


    # last cycle test to make sure we didn't fuck up
    # manual control test?
    # check for env metadata
    # make render optional test?
    # agent selection stuff
    # observe loop
    # make sure spaces are finite

    # add messages for everything?
    # look at my PR to SB and what they actually used