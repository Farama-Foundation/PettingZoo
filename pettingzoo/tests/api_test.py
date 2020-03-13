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
            warnings.warn("Observation has more than 3 dimensions")
        if observation.shape == (0,):
            assert False, "Observation can not be an empty array"
        if observation.shape == (1,):
            warnings.warn("Observation is a single number")
        if not isinstance(observation, observation_0.__class__):
            warnings.warn("Observations between agents are different classes")
        if (observation.shape != observation_0.shape) and (len(observation.shape) == len(observation_0.shape)):
            warnings.warn("Observations are different shapes")
        if len(observation.shape) != len(observation_0.shape):
            warnings.warn("Observations have different number of dimensions")
        if not np.can_cast(observation.dtype, np.dtype("float64")):
            warnings.warn("Observation numpy array is not a numeric dtype")
        if np.array_equal(observation, np.zeros(observation.shape)):
            warnings.warn("Observation numpy array is all zeros.")
        if not np.all(observation >= 0):
            warnings.warn("Observation contains negative numbers. This is bad in many environments.")
    else:
        warnings.warn("Observation is not NumPy array")


def test_observation_action_spaces(env, agent_0):
    assert isinstance(env.action_spaces, dict), "action_spaces must be a dict"
    assert isinstance(env.observation_spaces, dict), "observation_spaces must be a dict"
    assert len(env.observation_spaces) == len(env.action_spaces) == len(env.agents), "observation_spaces, action_spaces, and agents must have the same length"

    for agent in env.agents:
        assert isinstance(env.observation_spaces[agent], gym.spaces.Space), "Observation space for each agent must extend gym.spaces.Space"
        assert isinstance(env.action_spaces[agent], gym.spaces.Space), "Agent space for each agent must extend gym.spaces.Space"
        if not (isinstance(env.observation_spaces[agent], gym.spaces.Box) or isinstance(env.observation_spaces[agent], gym.spaces.Discrete)):
            warnings.warn("Observation space for each agent probably should be gym.spaces.box or gym.spaces.discrete")
        if not (isinstance(env.action_spaces[agent], gym.spaces.Box) or isinstance(env.action_spaces[agent], gym.spaces.Discrete)):
            warnings.warn("Action space for each agent probably should be gym.spaces.box or gym.spaces.discrete")
        if (not isinstance(agent, int)) and agent != 'env':
            warnings.warn("Agent's are recommended to have integer names")
        if not isinstance(env.observation_spaces[agent], env.observation_spaces[agent_0].__class__):
            warnings.warn("The class of observation spaces is different between two agents")
        if not isinstance(env.action_spaces[agent], env.action_spaces[agent_0].__class__):
            warnings.warn("The class of action spaces is different between two agents")
        if env.observation_spaces[agent] != env.observation_spaces[agent_0]:
            warnings.warn("Agents have different observation space sizes")
        if env.action_spaces[agent] != env.action_spaces[agent_0]:
            warnings.warn("Agents have different action space sizes")
        if isinstance(env.action_spaces[agent], gym.spaces.Box):
            if np.any(np.equal(env.action_spaces[agent].low, -np.inf)):
                warnings.warn("Agent's minimum action space value is -infinity. This is probably too low.")
            if np.any(np.equal(env.action_spaces[agent].high, np.inf)):
                warnings.warn("Agent's maxmimum action space value is infinity. This is probably too high")
            if np.any(np.equal(env.action_spaces[agent].low, env.action_spaces[agent].high)):
                warnings.warn("Agent's maximum and minimum action space values are equal")
            if np.any(np.greater(env.action_spaces[agent].low, env.action_spaces[agent].high)):
                assert False, "Agent's minimum action space value is greater than it's maximum"
            if env.action_spaces[agent].low.shape != env.action_spaces[agent].shape:
                assert False, "Agent's action_space.low and action_space have different shapes"

        if isinstance(env.observation_spaces[agent], gym.spaces.Box):
            if np.any(np.equal(env.observation_spaces[agent].low, -np.inf)):
                warnings.warn("Agent's minimum observation space value is -infinity. This is probably too low.")
            if np.any(np.equal(env.observation_spaces[agent].high, np.inf)):
                warnings.warn("Agent's maxmimum observation space value is infinity. This is probably too high")
            if np.any(np.equal(env.observation_spaces[agent].low, env.observation_spaces[agent].high)):
                warnings.warn("Agent's maximum and minimum observation space values are equal")
            if np.any(np.greater(env.observation_spaces[agent].low, env.observation_spaces[agent].high)):
                assert False, "Agent's minimum observation space value is greater than it's maximum"
            if env.observation_spaces[agent].low.shape != env.observation_spaces[agent].shape:
                assert False, "Agent's observation_space.low and observation_space have different shapes"


def test_reward(reward):
    if not (isinstance(reward, int) or isinstance(reward, float)) and not isinstance(np.dtype(reward), np.dtype) and not isinstance(reward, np.ndarray):
        warnings.warn("Reward should be int, float, NumPy dtype or NumPy array")
    if isinstance(reward, np.ndarray):
        if isinstance(reward, np.ndarray) and not reward.shape == (1,):
            assert False, "Rewards can only be one number"
        if np.isinf(reward):
            assert False, "Reward must be finite"
        if np.isnan(reward):
            assert False, "Rewards cannot be NaN"
        if not np.can_cast(reward.dtype, np.dtype("float64")):
            assert False, "Reward NumPy array is not a numeric dtype"


def test_rewards_dones(env, agent_0):
    for agent in env.agents:
        assert isinstance(env.dones[agent], bool), "Agent's values in dones must be True or False"
        assert isinstance(env.rewards[agent], env.rewards[agent_0].__class__), "Rewards for each agent must be of the same class"
        test_reward(env.rewards[agent])


def play_test(env, observation_0):
    prev_observe = env.reset()
    for agent in env.agent_order:  # step through every agent once with observe=True
        action = env.action_spaces[agent].sample()
        next_observe = env.step(action)
        assert env.observation_spaces[agent].contains(prev_observe), "Agent's observation is outside of it's observation space"
        test_obervation(prev_observe, observation_0)
        prev_observe = next_observe

    env.reset()
    reward_0 = env.rewards[env.agent_order[0]]
    for agent in env.agent_order:  # step through every agent once with observe=False
        action = env.action_spaces[agent].sample()
        reward, done, info = env.last()
        assert isinstance(done, bool), "last done is not True or False"
        assert reward == env.rewards[agent], "last reward and rewards[agent] do not match"
        assert done == env.dones[agent], "last done and rewards[done] do not match"
        assert isinstance(env.rewards[agent], reward_0.__class__), "Rewards for each agent must be of the same class"
        test_reward(reward)
        observation = env.step(action, observe=False)
        assert observation is None, "step(observe=False) must not return anything"


def test_observe(env, observation_0):
    for agent in env.agent_order:
        observation = env.observe(agent)
        test_obervation(observation, observation_0)


def test_render(env):
    render_modes = env.metadata.get('render.modes')
    assert render_modes is not None, "Environment's that support rendering must define render modes in metadata"
    for mode in render_modes:
        for agent in env.agent_order:
            action = env.action_spaces[agent].sample()
            env.step(action, observe=False)
            env.render(mode=mode)


def test_manual_control(env):
    pass


def api_test(env, render=False, manual_control=False):
    print("Starting API test")
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

    test_rewards_dones(env, agent_0)

    test_observe(env, observation_0)

    if render:
        test_render(env)

    if manual_control:
        test_manual_control(env)

    env.close()

    print("Passed API test")  # You only get here if you don't fail
