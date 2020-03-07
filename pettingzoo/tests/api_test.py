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
            assert False, "Observation can not be an empty array"
        if observation.shape == (1,):
            warnings.warn("Observation is a single number")
        if not isinstance(observation, observation_0):
            warnings.warn("Observations between agents are different classes")
        if (observation.shape != observation_0.shape) and (len(observation.shape) == len(observation_0.shape)):
            warnings.warn("Observations are different shapes")
        if len(observation.shape) != len(observation_0.shape):
            warnings.warn("Observations have different number of deminsions")
        if (observation.dtype != np.dtype('f')) and (observation.dtype != np.dtype('u')) and (observation.dtype != np.dtype('i')):
            warnings.warn("Observation numpy array is not a numeric dtype")
    else:
        warnings.warn("Observation is not NumPy array")


def test_observation_action_spaces(env, agent_0):
    assert isinstance(env.action_spaces, dict), "action_spaces must be a dict"
    assert isinstance(env.observation_spaces, dict), "observation_spaces must be a dict"
    assert len(env.observation_spaces) == len(env.action_spaces) == len(env.agents), "observation_spaces, action_spaces, and agents must have the same length"

    for agent in env.agents:
        if not (isinstance(env.observation_spaces[agent], gym.spaces.box) or isinstance(env.observation_spaces[agent], gym.spaces.discrete)):
            warnings.warn("Observation space for each agent should be gym.spaces.box or gym.spaces.discrete")
        if not (isinstance(env.action_spaces[agent], gym.spaces.box) or isinstance(env.action_spaces[agent], gym.spaces.discrete)):
            warnings.warn("Action space for each agent should be gym.spaces.box or gym.spaces.discrete")
        if (not isinstance(agent, int)) and agent != 'env':
            warnings.warn("Agent's are recommended to have integer names")
        if not isinstance(env.observation_spaces[agent], env.observation_spaces[agent_0]):
            warnings.warn("The class of observation spaces is different between two agents")
        if not isinstance(env.action_spaces[agent], env.action_spaces[agent_0]):
            warnings.warn("The class of action spaces is different between two agents")
        if env.observation_spaces[agent] != env.observation_spaces[agent_0]:
            warnings.warn("Agents have different observation space sizes")
        if env.action_spaces[agent] != env.action_spaces[agent_0]:
            warnings.warn("Agents have different observation space sizes")
        if isinstance(env.action_spaces[agent], gym.spaces.box):
            if env.action_spaces[agent].low == -np.inf:
                warnings.warn("Agent's minimum action space value is -infinity. This is probably too low.")
            if env.action_spaces[agent].high == np.inf:
                warnings.warn("Agent's maxmimum action space value is infinity. This is probably too high")
            if env.action_spaces[agent].low == env.action_spaces[agent].high:
                assert False, "Agent's maximum and minimum action space values are equal"
            if env.action_spaces[agent].low > env.action_spaces[agent].high:
                assert False, "Agent's mimum action space value is greater than it's maximum"

        if isinstance(env.observation_spaces[agent], gym.spaces.box):
            if env.observation_spaces[agent].low == -np.inf:
                warnings.warn("Agent's minimum observation space value is -infinity. This is probably too low.")
            if env.observation_spaces[agent].high == np.inf:
                warnings.warn("Agent's maxmimum observation space value is infinity. This is probably too high")
            if env.observation_spaces[agent].low == env.observation_spaces[agent].high:
                assert False, "Agent's maximum and minimum observation space values are equal"
            if env.observationn_spaces[agent].low > env.observation_spaces[agent].high:
                assert False, "Agent's mimum observation space value is greater than it's maximum"


def test_rewards(env, agent_0):
    for agent in env.agents:
        assert isinstance(env.dones[agent], bool), "Agent's values in dones must be True or False"

        if not ((isinstance(env.rewards[agent], int) or isinstance(env.rewards[agent], float)) and not isinstance(env.rewards[agent], np.ndarray)):
            warnings.warn("Reward should be int, float, or numpy array")
        if isinstance(env.rewards[agent], np.ndarray):
            if isinstance(env.rewards[agent], np.ndarray) and not env.rewards[agent].shape == (1,):
                assert False, "Rewards can only be one number"
            if np.isinf(env.rewards[agent]):
                assert False, "Reward must be finite"
            if np.isnan(env.rewards[agent]):
                assert False, "Rewards cannot be NaN"

        assert isinstance(env.rewards[agent], env.rewards[agent_0]), "Rewards for each agent must be of the same class"


def play_test(env, observation_0):
    for agent in env.agent_order:  # step through every agent once with observe=True
        action = env.action_spaces[agent].sample()
        observation = env.step(action)
        assert env.observation_spaces[agent].contains(observation), "Agent's observation is outside of it's observation space"
        test_obervation(observation, observation_0)

    for agent in env.agent_order:  # step through every agent once with observe=False
        action = env.action_spaces[agent].sample()
        observation = env.step(action, observe=False)
        assert observation is None, "step(observe=False) must not return anything"


def test_observe(env, observation_0):
    for agent in env.agent_order:
        observation = env.observe(agent)
        test_obervation(observation, observation_0)


def test_render(env):
    for agent in env.agent_order:
        env.step(observation=False)
        env.render()
    env.close()


def test_manual_control(env):
    pass


def api_test(env, render=False, manual_control=False):
    if manual_control:
        assert render, "Rendering must be enabled to test manual control"
    assert isinstance(env, pettingzoo.AECEnv), "Env must be an instance of pettingzoo.AECEnv"

    observation = env.reset(observe=False)
    assert observation is None, "reset(observe=False) must not return anything"

    observation_0 = env.reset()
    test_obervation(observation_0, observation_0)

    assert isinstance(env.agent_order, list), "agent_order must be a list"

    agent_0 = env.agent_order[0]

    test_observation_action_spaces(env, agent_0)

    play_test(env, observation_0)

    assert isinstance(env.rewards, dict), "rewards must be a dict"
    assert isinstance(env.dones, dict), "dones must be a dict"
    assert isinstance(env.infos, dict), "infos must be a dict"

    assert len(env.rewards) == len(env.dones) == len(env.infos) == len(env.agents), "rewards, dones, infos and agents must have the same length"

    test_rewards(env, agent_0)

    test_observe(env, observation_0)

    test_render(env)

    test_manual_control(env)

    # does env state get pass as an argument?
    # last cycle test to make sure we didn't fuck up
    # manual control test?
    # check for env metadata
    # agent selection stuff
    # look at my PR to SB and what they actually used
