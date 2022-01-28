import random
import re
import warnings
from collections import defaultdict

import gym
import numpy as np

import pettingzoo
from pettingzoo.utils.conversions import aec_to_parallel_wrapper, parallel_to_aec_wrapper
from pettingzoo.utils.wrappers import BaseWrapper

missing_attr_warning = '''This environment does not have {name} defined.
This is not a required part 'of the API as environments with procedurally
generated agents cannot always have this property defined. However, this is
very uncommon and these features should be included whenever possible as all
standard learning code requires these properties. Also not that if you do not
have {name} it should also not be possible for you to expose the possible_agents
list and observation_spaces, action_spaces dictionaries.'''


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
    for agent in env.agents:
        assert isinstance(env.observation_space(agent), gym.spaces.Space), "Observation space for each agent must extend gym.spaces.Space"
        assert isinstance(env.action_space(agent), gym.spaces.Space), "Agent space for each agent must extend gym.spaces.Space"
        assert env.observation_space(agent) is env.observation_space(agent), "observation_space should return the exact same space object (not a copy) for an agent. Consider decorating your observation_space(self, agent) method with @functools.lru_cache(maxsize=None)"
        assert env.action_space(agent) is env.action_space(agent), "action_space should return the exact same space object (not a copy) for an agent (ensures that action space seeding works as expected). Consider decorating your action_space(self, agent) method with @functools.lru_cache(maxsize=None)"
        if not (isinstance(env.observation_space(agent), gym.spaces.Box) or isinstance(env.observation_space(agent), gym.spaces.Discrete)):
            warnings.warn("Observation space for each agent probably should be gym.spaces.box or gym.spaces.discrete")
        if not (isinstance(env.action_space(agent), gym.spaces.Box) or isinstance(env.action_space(agent), gym.spaces.Discrete)):
            warnings.warn("Action space for each agent probably should be gym.spaces.box or gym.spaces.discrete")
        if (not isinstance(agent, str)) and agent != 'env':
            warnings.warn("Agent's are recommended to have numbered string names, like player_0")
        if not isinstance(agent, str) or not re.match("[a-z]+_[0-9]+", agent):  # regex for ending in _<integer>
            warnings.warn("We recommend agents to be named in the format <descriptor>_<number>, like \"player_0\"")
        if not isinstance(env.observation_space(agent), env.observation_space(agent_0).__class__):
            warnings.warn("The class of observation spaces is different between two agents")
        if not isinstance(env.action_space(agent), env.action_space(agent).__class__):
            warnings.warn("The class of action spaces is different between two agents")
        if env.observation_space(agent) != env.observation_space(agent_0):
            warnings.warn("Agents have different observation space sizes")
        if env.action_space(agent) != env.action_space(agent):
            warnings.warn("Agents have different action space sizes")

        if isinstance(env.action_space(agent), gym.spaces.Box):
            if np.any(np.equal(env.action_space(agent).low, -np.inf)):
                warnings.warn("Agent's minimum action space value is -infinity. This is probably too low.")
            if np.any(np.equal(env.action_space(agent).high, np.inf)):
                warnings.warn("Agent's maxmimum action space value is infinity. This is probably too high")
            if np.any(np.equal(env.action_space(agent).low, env.action_space(agent).high)):
                warnings.warn("Agent's maximum and minimum action space values are equal")
            if np.any(np.greater(env.action_space(agent).low, env.action_space(agent).high)):
                assert False, "Agent's minimum action space value is greater than it's maximum"
            if env.action_space(agent).low.shape != env.action_space(agent).shape:
                assert False, "Agent's action_space.low and action_space have different shapes"
            if env.action_space(agent).high.shape != env.action_space(agent).shape:
                assert False, "Agent's action_space.high and action_space have different shapes"

        if isinstance(env.observation_space(agent), gym.spaces.Box):
            if np.any(np.equal(env.observation_space(agent).low, -np.inf)):
                warnings.warn("Agent's minimum observation space value is -infinity. This is probably too low.")
            if np.any(np.equal(env.observation_space(agent).high, np.inf)):
                warnings.warn("Agent's maxmimum observation space value is infinity. This is probably too high")
            if np.any(np.equal(env.observation_space(agent).low, env.observation_space(agent).high)):
                warnings.warn("Agent's maximum and minimum observation space values are equal")
            if np.any(np.greater(env.observation_space(agent).low, env.observation_space(agent).high)):
                assert False, "Agent's minimum observation space value is greater than it's maximum"
            if env.observation_space(agent).low.shape != env.observation_space(agent).shape:
                assert False, "Agent's observation_space.low and observation_space have different shapes"
            if env.observation_space(agent).high.shape != env.observation_space(agent).shape:
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
        float(env.rewards[agent])  # "Rewards for each agent must be convertible to float
        test_reward(env.rewards[agent])


def play_test(env, observation_0, num_cycles):
    '''
    plays through environment and does dynamic checks to make
    sure the state returned by the environment is
    consistent. In particular it checks:

    * Whether the reward returned by last is the accumulated reward
    * Whether the agents list shrinks when agents are done
    * Whether the keys of the rewards, dones, infos are equal to the agents list
    * tests that the observation is in bounds.
    '''
    env.reset()

    done = {agent: False for agent in env.agents}
    live_agents = set(env.agents[:])
    has_finished = set()
    generated_agents = set()
    accumulated_rewards = defaultdict(int)
    for agent in env.agent_iter(env.num_agents * num_cycles):
        generated_agents.add(agent)
        assert agent not in has_finished, "agents cannot resurect! Generate a new agent with a new name."
        assert isinstance(env.infos[agent], dict), "an environment agent's info must be a dictionary"
        prev_observe, reward, done, info = env.last()
        if done:
            action = None
        elif isinstance(prev_observe, dict) and 'action_mask' in prev_observe:
            action = random.choice(np.flatnonzero(prev_observe['action_mask']))
        else:
            action = env.action_space(agent).sample()

        if agent not in live_agents:
            live_agents.add(agent)

        assert live_agents.issubset(set(env.agents)), "environment must delete agents as the game continues"

        if done:
            live_agents.remove(agent)
            has_finished.add(agent)

        assert accumulated_rewards[agent] == reward, "reward returned by last is not the accumulated rewards in its rewards dict"
        accumulated_rewards[agent] = 0

        env.step(action)

        for a, rew in env.rewards.items():
            accumulated_rewards[a] += rew

        assert env.num_agents == len(env.agents), "env.num_agents is not equal to len(env.agents)"
        assert set(env.rewards.keys()) == (set(env.agents)), "agents should not be given a reward if they were done last turn"
        assert set(env.dones.keys()) == (set(env.agents)), "agents should not be given a done if they were done last turn"
        assert set(env.infos.keys()) == (set(env.agents)), "agents should not be given an info if they were done last turn"
        if hasattr(env, 'possible_agents'):
            assert set(env.agents).issubset(set(env.possible_agents)), "possible agents should always include all agents, if it exists"

        if not env.agents:
            break

        if isinstance(env.observation_space(agent), gym.spaces.Box):
            assert env.observation_space(agent).dtype == prev_observe.dtype
        assert env.observation_space(agent).contains(prev_observe), \
            ("Out of bounds observation: " + str(prev_observe))

        assert env.observation_space(agent).contains(prev_observe), "Agent's observation is outside of it's observation space"
        test_observation(prev_observe, observation_0)
        if not isinstance(env.infos[env.agent_selection], dict):
            warnings.warn("The info of each agent should be a dict, use {} if you aren't using info")

    if not env.agents:
        assert has_finished == generated_agents, "not all agents finished, some were skipped over"

    env.reset()
    for agent in env.agent_iter(env.num_agents * 2):
        obs, reward, done, info = env.last()
        if done:
            action = None
        elif isinstance(obs, dict) and 'action_mask' in obs:
            action = random.choice(np.flatnonzero(obs['action_mask']))
        else:
            action = env.action_space(agent).sample()
        assert isinstance(done, bool), "Done from last is not True or False"
        assert done == env.dones[agent], "Done from last() and dones[agent] do not match"
        assert info == env.infos[agent], "Info from last() and infos[agent] do not match"
        float(env.rewards[agent])  # "Rewards for each agent must be convertible to float
        test_reward(reward)
        observation = env.step(action)
        assert observation is None, "step() must not return anything"


def test_action_flexibility(env):
    env.reset()
    agent = env.agent_selection
    action_space = env.action_space(agent)
    if isinstance(action_space, gym.spaces.Discrete):
        obs, reward, done, info = env.last()
        if done:
            action = None
        elif isinstance(obs, dict) and 'action_mask' in obs:
            action = random.choice(np.flatnonzero(obs['action_mask']))
        else:
            action = 0
        env.step(action)
        env.reset()
        env.step(np.int32(action))
    elif isinstance(action_space, gym.spaces.Box):
        env.step(np.zeros_like(action_space.low))
        env.reset()
        env.step(np.zeros_like(action_space.low))


def api_test(env, num_cycles=10, verbose_progress=False):
    def progress_report(msg):
        if verbose_progress:
            print(msg)

    print("Starting API test")
    if not hasattr(env, 'possible_agents'):
        warnings.warn(missing_attr_warning.format(name='possible_agents'))

    env.reset()

    assert isinstance(env, pettingzoo.AECEnv), "Env must be an instance of pettingzoo.AECEnv"

    env.reset()
    assert not any(env.dones.values()), "dones must all be False after reset"

    assert isinstance(env.num_agents, int), "num_agents must be an integer"
    assert env.num_agents != 0, "An environment should have a nonzero number of agents"
    assert env.num_agents > 0, "An environment should have a positive number of agents"

    env.reset()
    observation_0, _, _, _ = env.last()
    test_observation(observation_0, observation_0)

    non_observe, _, _, _ = env.last(observe=False)
    assert non_observe is None, "last must return a None when observe=False"

    progress_report("Finished test_observation")

    agent_0 = env.agent_selection

    test_observation_action_spaces(env, agent_0)

    progress_report("Finished test_observation_action_spaces")

    play_test(env, observation_0, num_cycles)

    progress_report("Finished play test")

    assert isinstance(env.rewards, dict), "rewards must be a dict"
    assert isinstance(env.dones, dict), "dones must be a dict"
    assert isinstance(env.infos, dict), "infos must be a dict"

    assert len(env.rewards) == len(env.dones) == len(env.infos) == len(env.agents), "rewards, dones, infos and agents must have the same length"

    test_rewards_dones(env, agent_0)

    test_action_flexibility(env)

    progress_report("Finished test_rewards_dones")

    # checks unwrapped attribute
    assert not isinstance(env.unwrapped, aec_to_parallel_wrapper)
    assert not isinstance(env.unwrapped, parallel_to_aec_wrapper)
    assert not isinstance(env.unwrapped, BaseWrapper)

    # Test that if env has overridden render(), they must have overridden close() as well
    base_render = pettingzoo.utils.env.AECEnv.render
    base_close = pettingzoo.utils.env.AECEnv.close
    if base_render != env.__class__.render:
        assert (base_close != env.__class__.close), "If render method defined, then close method required"
    else:
        warnings.warn("Environment has not defined a render() method")

    print("Passed API test")
