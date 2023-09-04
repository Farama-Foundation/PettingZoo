from __future__ import annotations

import re
import warnings
from collections import defaultdict

import gymnasium
import numpy as np

import pettingzoo
from pettingzoo.utils.conversions import (
    aec_to_parallel_wrapper,
    parallel_to_aec_wrapper,
)
from pettingzoo.utils.wrappers import BaseWrapper

try:
    """Allows doctests to be run using pytest"""
    import pytest

    from pettingzoo.test.example_envs import generated_agents_env_v0

    @pytest.fixture
    def env():
        env = generated_agents_env_v0.env()
        env.reset()
        return env

    @pytest.fixture
    def env_name():
        return "generated_agents_env_v0"

    @pytest.fixture()
    def observation(env):
        return env.observation_space(env.agents[0]).sample()

    @pytest.fixture()
    def observation_0(env):
        return env.observation_space(env.agents[1]).sample()

    @pytest.fixture
    def reward():
        return 0

    @pytest.fixture
    def agent_0():
        env = generated_agents_env_v0.env()
        env.reset()
        return env.agents[0]

    from pettingzoo.classic import connect_four_v3

    @pytest.fixture
    def action_mask():
        env = connect_four_v3.env()
        env.reset()
        return env.observation_space(env.agents[0]).sample()["action_mask"]

except ModuleNotFoundError:
    pass

missing_attr_warning = """This environment does not have {name} defined.
This is not a required part 'of the API as environments with procedurally
generated agents cannot always have this property defined. However, this is
very uncommon and these features should be included whenever possible as all
standard learning code requires these properties. Also not that if you do not
have {name} it should also not be possible for you to expose the possible_agents
list and observation_spaces, action_spaces dictionaries."""
env_obs_dicts = [
    "leduc_holdem_v4",
    "texas_holdem_no_limit_v6",
    "texas_holdem_v4",
    "go_v5",
    "chess_v6",
    "connect_four_v3",
    "tictactoe_v3",
    "gin_rummy_v4",
]
env_graphical_obs = ["knights_archers_zombies_v10"]
env_diff_obs_shapes = [
    "simple_adversary_v3",
    "simple_world_comm_v3",
    "simple_tag_v3",
    "knights_archers_zombies_v10",
    "simple_push_v3",
    "simple_speaker_listener_v4",
    "simple_crypto_v3",
]
env_all_zeros_obs = ["knights_archers_zombies_v10"]
env_obs_space = [
    "leduc_holdem_v4",
    "texas_holdem_no_limit_v6",
    "texas_holdem_v4",
    "go_v5",
    "hanabi_v5",
    "knights_archers_zombies_v10",
    "chess_v6",
    "connect_four_v3",
    "tictactoe_v3",
    "gin_rummy_v4",
]
env_diff_agent_obs_size = [
    "simple_adversary_v3",
    "simple_world_comm_v3",
    "simple_tag_v3",
    "simple_crypto_v3",
    "simple_push_v3",
    "simple_speaker_listener_v4",
]
env_pos_inf_obs = [
    "simple_adversary_v3",
    "simple_reference_v3",
    "simple_spread_v3",
    "simple_tag_v3",
    "simple_world_comm_v3",
    "multiwalker_v9",
    "simple_crypto_v3",
    "simple_push_v3",
    "simple_speaker_listener_v4",
    "simple_v3",
]
env_neg_inf_obs = [
    "simple_adversary_v3",
    "simple_reference_v3",
    "simple_spread_v3",
    "simple_tag_v3",
    "simple_world_comm_v3",
    "multiwalker_v9",
    "simple_crypto_v3",
    "simple_push_v3",
    "simple_speaker_listener_v4",
    "simple_v3",
]


def test_observation(observation, observation_0, env_name=None):
    if not isinstance(observation, np.ndarray):
        if env_name is not None and env_name not in env_obs_dicts:
            warnings.warn("Observation is not a NumPy array")
        if isinstance(observation, dict) and "observation" in observation.keys():
            observation = observation["observation"]
            test_observation(observation, observation_0, env_name)
        if isinstance(observation, dict) and "action_mask" in observation.keys():
            test_action_mask(observation["action_mask"], env_name)
        return
    if np.isinf(observation).any():
        warnings.warn(
            "Observation contains infinity (np.inf) or negative infinity (-np.inf)"
        )
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
    if (
        (observation.shape != observation_0.shape)
        and (len(observation.shape) == len(observation_0.shape))
        and env_name not in env_diff_obs_shapes
    ):
        warnings.warn("Observations are different shapes")
    if len(observation.shape) != len(observation_0.shape):
        warnings.warn("Observations have different number of dimensions")
    if not np.can_cast(observation.dtype, np.dtype("float64")):
        warnings.warn("Observation numpy array is not a numeric dtype")
    if (
        np.array_equal(observation, np.zeros(observation.shape))
        and env_name not in env_all_zeros_obs
    ):
        warnings.warn("Observation numpy array is all zeros.")
    if (
        not np.all(observation >= 0)
        and (
            (len(observation.shape) == 2)
            or (len(observation.shape) == 3 and observation.shape[2] == 1)
            or (len(observation.shape) == 3 and observation.shape[2] == 3)
        )
        and env_name not in env_graphical_obs
    ):
        warnings.warn(
            "The observation contains negative numbers and is in the shape of a graphical observation. This might be a bad thing."
        )


def test_action_mask(action_mask, env_name=None):
    if not isinstance(action_mask, np.ndarray):
        warnings.warn("Action mask is not a NumPy array")
        return
    if np.isinf(action_mask).any():
        warnings.warn(
            "Action mask contains infinity (np.inf) or negative infinity (-np.inf)"
        )
    if np.isnan(action_mask).any():
        warnings.warn("Action mask contains NaNs")
    if len(action_mask.shape) > 1:
        warnings.warn("Action mask has more than 1 dimension")
    if action_mask.shape == (0,):
        assert False, "Action mask can not be an empty array"
    if action_mask.shape == (1,):
        warnings.warn("Action mask is a single number")
    if not np.can_cast(action_mask.dtype, np.dtype("float64")):
        warnings.warn("Action mask numpy array is not a numeric dtype")
    if (
        np.array_equal(action_mask, np.zeros(action_mask.shape))
        and env_name not in env_all_zeros_obs
    ):
        warnings.warn("Action mask numpy array is all zeros (no legal actions).")
    if not np.array_equal(action_mask, action_mask.astype(bool)):
        warnings.warn(
            "Action mask is not boolean (contains values other than 0 and 1)."
        )


def test_observation_action_spaces(env, agent_0):
    for agent in env.agents:
        assert isinstance(
            env.observation_space(agent), gymnasium.spaces.Space
        ), "Observation space for each agent must extend gymnasium.spaces.Space"
        assert isinstance(
            env.action_space(agent), gymnasium.spaces.Space
        ), "Agent space for each agent must extend gymnasium.spaces.Space"
        assert env.observation_space(agent) is env.observation_space(agent), (
            "observation_space should return the exact same space object (not a copy) for an agent (ensures that observation space seeding works as expected). "
            "Consider decorating your observation_space(self, agent) method with @functools.lru_cache(maxsize=None) to enable caching, or changing it to read from a dict such as self.observation_spaces."
        )
        assert env.action_space(agent) is env.action_space(agent), (
            "action_space should return the exact same space object (not a copy) for an agent (ensures that action space seeding works as expected). "
            "Consider decorating your action_space(self, agent) method with @functools.lru_cache(maxsize=None) to enable caching, or changing it to read from a dict such as self.action_spaces."
        )
        if (
            not (
                isinstance(env.observation_space(agent), gymnasium.spaces.Box)
                or isinstance(env.observation_space(agent), gymnasium.spaces.Discrete)
            )
            and str(env.unwrapped) not in env_obs_space
        ):
            warnings.warn(
                "Observation space for each agent probably should be gymnasium.spaces.box or gymnasium.spaces.discrete"
            )
        if not (
            isinstance(env.action_space(agent), gymnasium.spaces.Box)
            or isinstance(env.action_space(agent), gymnasium.spaces.Discrete)
        ):
            warnings.warn(
                "Action space for each agent probably should be gymnasium.spaces.box or gymnasium.spaces.discrete"
            )
        if (not isinstance(agent, str)) and agent != "env":
            warnings.warn(
                "Agents are recommended to have numbered string names, like player_0"
            )
        if not isinstance(agent, str) or not re.match(
            "[a-z]+_[0-9]+", agent
        ):  # regex for ending in _<integer>
            warnings.warn(
                'We recommend agents to be named in the format <descriptor>_<number>, like "player_0"'
            )
        if not isinstance(
            env.observation_space(agent), env.observation_space(agent_0).__class__
        ):
            warnings.warn(
                "The class of observation spaces is different between two agents"
            )
        if not isinstance(env.action_space(agent), env.action_space(agent).__class__):
            warnings.warn("The class of action spaces is different between two agents")
        if (
            env.observation_space(agent) != env.observation_space(agent_0)
            and str(env.unwrapped) not in env_diff_agent_obs_size
        ):
            warnings.warn("Agents have different observation space sizes")
        if env.action_space(agent) != env.action_space(agent):
            warnings.warn("Agents have different action space sizes")

        if isinstance(env.action_space(agent), gymnasium.spaces.Box):
            if np.any(np.equal(env.action_space(agent).low, -np.inf)):
                warnings.warn(
                    "Agent's minimum action space value is -infinity. This is probably too low."
                )
            if np.any(np.equal(env.action_space(agent).high, np.inf)):
                warnings.warn(
                    "Agent's maximum action space value is infinity. This is probably too high"
                )
            if np.any(
                np.equal(env.action_space(agent).low, env.action_space(agent).high)
            ):
                warnings.warn(
                    "Agent's maximum and minimum action space values are equal"
                )
            if np.any(
                np.greater(env.action_space(agent).low, env.action_space(agent).high)
            ):
                assert (
                    False
                ), "Agent's minimum action space value is greater than it's maximum"
            if env.action_space(agent).low.shape != env.action_space(agent).shape:
                assert (
                    False
                ), "Agent's action_space.low and action_space have different shapes"
            if env.action_space(agent).high.shape != env.action_space(agent).shape:
                assert (
                    False
                ), "Agent's action_space.high and action_space have different shapes"

        if isinstance(env.observation_space(agent), gymnasium.spaces.Box):
            if (
                np.any(np.equal(env.observation_space(agent).low, -np.inf))
                and str(env.unwrapped) not in env_neg_inf_obs
            ):
                warnings.warn(
                    "Agent's minimum observation space value is -infinity. This is probably too low."
                )
            if (
                np.any(np.equal(env.observation_space(agent).high, np.inf))
                and str(env.unwrapped) not in env_pos_inf_obs
            ):
                warnings.warn(
                    "Agent's maximum observation space value is infinity. This is probably too high"
                )
            if np.any(
                np.equal(
                    env.observation_space(agent).low, env.observation_space(agent).high
                )
            ):
                warnings.warn(
                    "Agent's maximum and minimum observation space values are equal"
                )
            if np.any(
                np.greater(
                    env.observation_space(agent).low, env.observation_space(agent).high
                )
            ):
                assert (
                    False
                ), "Agent's minimum observation space value is greater than it's maximum"
            if (
                env.observation_space(agent).low.shape
                != env.observation_space(agent).shape
            ):
                assert (
                    False
                ), "Agent's observation_space.low and observation_space have different shapes"
            if (
                env.observation_space(agent).high.shape
                != env.observation_space(agent).shape
            ):
                assert (
                    False
                ), "Agent's observation_space.high and observation_space have different shapes"


def test_reward(reward):
    if (
        not (isinstance(reward, int) or isinstance(reward, float))
        and not isinstance(np.dtype(reward), np.dtype)
        and not isinstance(reward, np.ndarray)
    ):
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


def test_rewards_terminations_truncations(env, agent_0):
    for agent in env.agents:
        assert isinstance(
            env.terminations[agent], bool
        ), "Agent's values in terminations must be True or False"
        assert isinstance(
            env.truncations[agent], bool
        ), "Agent's values in truncations must be True or False"
        float(
            env.rewards[agent]
        )  # "Rewards for each agent must be convertible to float
        test_reward(env.rewards[agent])


def play_test(env, observation_0, num_cycles):
    """
    plays through environment and does dynamic checks to make
    sure the state returned by the environment is
    consistent. In particular it checks:

    * Whether the reward returned by last is the accumulated reward
    * Whether the agents list shrinks when agents are terminated or truncated
    * Whether the keys of the rewards, terminations, truncations, infos are equal to the agents list
    * tests that the observation is in bounds.
    """
    env.reset()

    live_agents = set(env.agents[:])
    has_finished = set()
    generated_agents = set()
    accumulated_rewards = defaultdict(int)
    for agent in env.agent_iter(env.num_agents * num_cycles):
        generated_agents.add(agent)
        assert (
            agent not in has_finished
        ), "agents cannot resurect! Generate a new agent with a new name."
        assert isinstance(
            env.infos[agent], dict
        ), "an environment agent's info must be a dictionary"
        prev_observe, reward, terminated, truncated, info = env.last()
        if terminated or truncated:
            action = None
        elif isinstance(prev_observe, dict) and "action_mask" in prev_observe:
            action = env.action_space(agent).sample(prev_observe["action_mask"])
        elif "action_mask" in info:
            action = env.action_space(agent).sample(info["action_mask"])
        else:
            action = env.action_space(agent).sample()

        if agent not in live_agents:
            live_agents.add(agent)

        assert live_agents.issubset(
            set(env.agents)
        ), "environment must delete agents as the game continues"

        if terminated or truncated:
            live_agents.remove(agent)
            has_finished.add(agent)

        assert (
            accumulated_rewards[agent] == reward
        ), "reward returned by last is not the accumulated rewards in its rewards dict"
        accumulated_rewards[agent] = 0

        env.step(action)

        for a, rew in env.rewards.items():
            accumulated_rewards[a] += rew

        assert env.num_agents == len(
            env.agents
        ), "env.num_agents is not equal to len(env.agents)"
        assert set(env.rewards.keys()) == (
            set(env.agents)
        ), "agents should not be given a reward if they were terminated or truncated last turn"
        assert set(env.terminations.keys()) == (
            set(env.agents)
        ), "agents should not be given a termination if they were terminated or truncated last turn"
        assert set(env.truncations.keys()) == (
            set(env.agents)
        ), "agents should not be given a truncation if they were terminated or truncated last turn"
        assert set(env.infos.keys()) == (
            set(env.agents)
        ), "agents should not be given an info if they were terminated or truncated last turn"
        if hasattr(env, "possible_agents"):
            assert set(env.agents).issubset(
                set(env.possible_agents)
            ), "possible agents should always include all agents, if it exists"

        if not env.agents:
            break

        assert env.observation_space(agent).contains(
            prev_observe
        ), "Out of bounds observation: " + str(prev_observe)

        if isinstance(env.observation_space(agent), gymnasium.spaces.Box):
            assert env.observation_space(agent).dtype == prev_observe.dtype
        elif isinstance(env.observation_space(agent), gymnasium.spaces.Dict):
            assert (
                env.observation_space(agent)["observation"].dtype
                == prev_observe["observation"].dtype
            )
        test_observation(prev_observe, observation_0, str(env.unwrapped))
        if not isinstance(env.infos[env.agent_selection], dict):
            warnings.warn(
                "The info of each agent should be a dict, use {} if you aren't using info"
            )

    if not env.agents:
        assert (
            has_finished == generated_agents
        ), "not all agents finished, some were skipped over"

    env.reset()
    for agent in env.agent_iter(env.num_agents * 2):
        obs, reward, terminated, truncated, info = env.last()
        if terminated or truncated:
            action = None
        elif isinstance(obs, dict) and "action_mask" in obs:
            action = env.action_space(agent).sample(obs["action_mask"])
        elif "action_mask" in info:
            action = env.action_space(agent).sample(info["action_mask"])
        else:
            action = env.action_space(agent).sample()
        assert isinstance(terminated, bool), "terminated from last is not True or False"
        assert isinstance(truncated, bool), "terminated from last is not True or False"
        assert (
            terminated == env.terminations[agent]
        ), "terminated from last() and terminations[agent] do not match"
        assert (
            truncated == env.truncations[agent]
        ), "truncated from last() and truncations[agent] do not match"
        assert (
            info == env.infos[agent]
        ), "Info from last() and infos[agent] do not match"
        float(
            env.rewards[agent]
        )  # "Rewards for each agent must be convertible to float
        test_reward(reward)
        observation = env.step(action)
        assert observation is None, "step() must not return anything"


def test_action_flexibility(env):
    """Tests that a given action is valid given a seeded environment reset"""
    env.reset(seed=0)
    agent = env.agent_selection
    action_space = env.action_space(agent)
    if isinstance(action_space, gymnasium.spaces.Discrete):
        obs, reward, terminated, truncated, info = env.last()
        if terminated or truncated:
            action = None
        elif isinstance(obs, dict) and "action_mask" in obs:
            action = env.action_space(agent).sample(obs["action_mask"])
        elif "action_mask" in info:
            action = env.action_space(agent).sample(info["action_mask"])
        else:
            action = 0
        env.step(action)
        env.reset(seed=0)
        env.step(np.int32(action))
    elif isinstance(action_space, gymnasium.spaces.Box):
        env.step(np.zeros_like(action_space.low))
        env.reset(seed=0)
        env.step(np.zeros_like(action_space.low))


def api_test(env, num_cycles=1000, verbose_progress=False):
    def progress_report(msg):
        if verbose_progress:
            print(msg)

    print("Starting API test")
    if not hasattr(env, "possible_agents"):
        warnings.warn(missing_attr_warning.format(name="possible_agents"))

    # checks that reset takes arguments called seed and options
    env.reset(seed=0, options={"options": 1})

    assert isinstance(
        env, pettingzoo.AECEnv
    ), "Env must be an instance of pettingzoo.AECEnv"

    env.reset()
    assert not any(
        env.terminations.values()
    ), "terminations must all be False after reset"
    assert not any(
        env.truncations.values()
    ), "truncations must all be False after reset"

    assert isinstance(env.num_agents, int), "num_agents must be an integer"
    assert env.num_agents != 0, "An environment should have a nonzero number of agents"
    assert env.num_agents > 0, "An environment should have a positive number of agents"

    env.reset()
    observation_0, *_ = env.last()
    if isinstance(observation_0, dict) and "observation" in observation_0:
        observation_0 = observation_0["observation"]

    test_observation(observation_0, observation_0, str(env.unwrapped))

    non_observe, *_ = env.last(observe=False)
    assert non_observe is None, "last must return a None when observe=False"

    progress_report("Finished test_observation")

    agent_0 = env.agent_selection

    test_observation_action_spaces(env, agent_0)

    progress_report("Finished test_observation_action_spaces")

    play_test(env, observation_0, num_cycles)

    progress_report("Finished play test")

    assert isinstance(env.rewards, dict), "rewards must be a dict"
    assert isinstance(env.terminations, dict), "terminations must be a dict"
    assert isinstance(env.truncations, dict), "truncations must be a dict"
    assert isinstance(env.infos, dict), "infos must be a dict"

    assert (
        len(env.rewards)
        == len(env.terminations)
        == len(env.truncations)
        == len(env.infos)
        == len(env.agents)
    ), "rewards, terminations, truncations, infos and agents must have the same length"

    test_rewards_terminations_truncations(env, agent_0)

    test_action_flexibility(env)

    progress_report("Finished test_rewards_terminations_truncations")

    # checks unwrapped attribute
    assert not isinstance(env.unwrapped, aec_to_parallel_wrapper)
    assert not isinstance(env.unwrapped, parallel_to_aec_wrapper)
    assert not isinstance(env.unwrapped, BaseWrapper)

    # Test that if env has overridden render(), they must have overridden close() as well
    base_render = pettingzoo.utils.env.AECEnv.render
    base_close = pettingzoo.utils.env.AECEnv.close
    if base_render != env.__class__.render:
        assert (
            base_close != env.__class__.close
        ), "If render method defined, then close method required"
    else:
        warnings.warn("Environment has not defined a render() method")

    print("Passed API test")
