import pettingzoo
from pettingzoo.utils import agent_selector
import warnings
import numpy as np
from copy import copy
import gym
import random
import re
import os


def test_observation(observation, observation_0):
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
        if not np.all(observation >= 0) and ((len(observation.shape) == 2) or (len(observation.shape) == 3 and observation.shape[2] == 1) or (len(observation.shape) == 3 and observation.shape[2] == 3)):
            warnings.warn("The observation contains negative numbers and is in the shape of a graphical observation. This might be a bad thing.")
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
        if (not isinstance(agent, str)) and agent != 'env':
            warnings.warn("Agent's are recommended to have numbered string names, like player_0")
        if not isinstance(agent, str) or not re.match("[a-z]+_[0-9]+", agent):  # regex for ending in _<integer>
            warnings.warn("We recommend agents to be named in the format <descriptor>_<number>, like \"player_0\"")
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
            if env.action_spaces[agent].high.shape != env.action_spaces[agent].shape:
                assert False, "Agent's action_space.high and action_space have different shapes"

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
            if env.observation_spaces[agent].high.shape != env.observation_spaces[agent].shape:
                assert False, "Agent's observation_space.high and observation_space have different shapes"


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
        print()
        print()
        print()
        print(agent_0 is env.agent_order[0])
        print('class')
        # print(env.rewards[agent_0])
        print(env.rewards[agent_0].__class__)
        print('class done')
        print()
        print()
        print()
        assert isinstance(env.rewards[agent], env.rewards[agent_0].__class__), "Rewards for each agent must be of the same class"
        test_reward(env.rewards[agent])


def play_test(env, observation_0):
    prev_observe = env.reset()
    for agent in env.agent_order:  # step through every agent once with observe=True
        if 'legal_moves' in env.infos[agent]:
            action = random.choice(env.infos[agent]['legal_moves'])
        else:
            action = env.action_spaces[agent].sample()
        next_observe = env.step(action)
        if not env.observation_spaces[agent].contains(prev_observe):
            print("Out of bounds observation: ", prev_observe)
        assert env.observation_spaces[agent].contains(prev_observe), "Agent's observation is outside of it's observation space"
        test_observation(prev_observe, observation_0)
        prev_observe = next_observe
        if not isinstance(env.infos[agent], dict):
            warnings.warn("The info of each agent should be a dict, use {} if you aren't using info")
        assert env.num_agents == len(env.agents), "env.num_agents is not equal to len(env.agents)"

    env.reset()
    reward_0 = env.rewards[env.agent_order[0]]
    for agent in env.agent_order:  # step through every agent once with observe=False
        if 'legal_moves' in env.infos[agent]:
            action = random.choice(env.infos[agent]['legal_moves'])
        else:
            action = env.action_spaces[agent].sample()
        reward, done, info = env.last()
        assert isinstance(done, bool), "Done from last is not True or False"
        assert reward == env.rewards[agent], "Reward from last() and rewards[agent] do not match"
        assert done == env.dones[agent], "Done from last() and rewards[agent] do not match"
        assert info == env.infos[agent], "Info from last() and infos[agent] do not match"
        assert isinstance(env.rewards[agent], reward_0.__class__), "Rewards for each agent must be of the same class"
        test_reward(reward)
        observation = env.step(action, observe=False)
        assert observation is None, "step(observe=False) must not return anything"


def test_agent_order(env):
    env.reset()
    if not hasattr(env, "_agent_selector"):
        warnings.warn("Env has no object named _agent_selector. We recommend handling agent cycling with the agent_selector utility from utils/agent_selector.py.")

    elif not isinstance(env._agent_selector, agent_selector):
        warnings.warn("You created your own agent_selector utility. You might want to use ours, in utils/agent_selector.py")

    assert hasattr(env, "agent_order"), "Env does not have agent_order"

    env.reset(observe=False)
    agent_order = copy(env.agent_order)
    _agent_selector = agent_selector(agent_order)
    agent_selection = _agent_selector.next()

    if hasattr(env, "_agent_selector"):
        assert env._agent_selector == _agent_selector, "env._agent_selector is initialized incorrectly"

    assert env.agent_selection == agent_selection, "env.agent_selection is not the same as the first agent in agent_order"

    for _ in range(200):
        agent = agent_selection
        if 'legal_moves' in env.infos[agent]:
            action = random.choice(env.infos[agent]['legal_moves'])
        else:
            action = env.action_spaces[agent].sample()
        env.step(action, observe=False)

        if all(env.dones.values()):
            break

        if agent_order == env.agent_order:
            agent_selection = _agent_selector.next()
            assert env.agent_selection == agent_selection, "env.agent_selection ({}) is not the same as the next agent in agent_order {}".format(env.agent_selection, env.agent_order)
        else:
            previous_agent_selection_index = agent_order.index(agent_selection)
            agent_order = copy(env.agent_order)
            _agent_selector.reinit(agent_order)
            skips = (previous_agent_selection_index + 1) % len(env.agents)
            for _ in range(skips + 1):
                agent_selection = _agent_selector.next()
            assert env.agent_selection == agent_selection, "env.agent_selection ({}) is not the same as the next agent in agent_order {}".format(env.agent_selection, env.agent_order)


def api_test(env, render=False, verbose_progress=False):
    def progress_report(msg):
        if verbose_progress:
            print(msg)

    print("Starting API test")
    env_agent_sel = copy(env)

    env.reset()

    assert isinstance(env, pettingzoo.AECEnv), "Env must be an instance of pettingzoo.AECEnv"

    # do this before reset
    observation = env.reset(observe=False)
    assert observation is None, "reset(observe=False) must not return anything"
    assert not any(env.dones.values()), "dones must all be False after reset"

    assert isinstance(env.num_agents, int), "num_agents must be an integer"
    assert env.num_agents != 0, "Your environment should have a nonzero number of agents"
    assert env.num_agents > 0, "Your environment can't have a negative number of agents"

    observation_0 = env.reset()
    test_observation(observation_0, observation_0)

    progress_report("Finished test_observation")

    assert isinstance(env.agent_order, list), "agent_order must be a list"

    agent_0 = env.agent_order[0]

    test_observation_action_spaces(env, agent_0)

    progress_report("Finished test_observation_action_spaces")

    play_test(env, observation_0)

    progress_report("Finished play test")

    assert isinstance(env.rewards, dict), "rewards must be a dict"
    assert isinstance(env.dones, dict), "dones must be a dict"
    assert isinstance(env.infos, dict), "infos must be a dict"

    assert len(env.rewards) == len(env.dones) == len(env.infos) == len(env.agents), "rewards, dones, infos and agents must have the same length"

    test_rewards_dones(env, agent_0)

    progress_report("Finished test_rewards_dones")

    test_agent_order(env_agent_sel)

    progress_report("Finished test_agent_order")

    # test that if env has overridden render(), they must have overridden close() as well
    base_render = pettingzoo.utils.env.AECEnv.render
    base_close = pettingzoo.utils.env.AECEnv.close
    if base_render != env.__class__.render:
        assert (base_close != env.__class__.close), "If render method defined, then close method required"
    else:
        warnings.warn("Environment has not defined a render() method")

    print("Passed API test")
