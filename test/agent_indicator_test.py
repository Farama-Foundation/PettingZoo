from __future__ import annotations

from typing import Any

import gymnasium.spaces
import numpy as np
import pytest

from pettingzoo.utils.conversions import parallel_to_aec
from pettingzoo.utils.env import ParallelEnv
from pettingzoo.utils.wrappers import AgentIndicatorParallelV1, AgentIndicatorV1

AGENTS = ["predator_0", "predator_1", "prey_0"]


class IndicatorEnv(ParallelEnv[str, Any, int]):
    metadata = {"name": "indicator_test"}
    render_mode = None

    def __init__(self, observation_space, observation):
        self.possible_agents = AGENTS[:]
        self._observation_space = observation_space
        self._action_space = gymnasium.spaces.Discrete(2)
        self._observation = observation

    def observation_space(self, agent):
        return self._observation_space

    def action_space(self, agent):
        return self._action_space

    def _observations(self):
        return {agent: self._observation.copy() for agent in self.agents}

    def reset(self, seed=None, options=None):
        self.agents = self.possible_agents[:]
        return self._observations(), {agent: {} for agent in self.agents}

    def step(self, actions):
        self._observation = self._observation + 1
        return (
            self._observations(),
            dict.fromkeys(self.agents, 0.0),
            dict.fromkeys(self.agents, False),
            dict.fromkeys(self.agents, False),
            {agent: {} for agent in self.agents},
        )


@pytest.mark.parametrize("shape", [(2,), (2, 1), (2, 1, 2)])
def test_aec_box_agent_indicators(shape) -> None:
    observation = np.ones(shape, dtype=np.float32)
    space = gymnasium.spaces.Box(low=0, high=2, shape=shape, dtype=np.float32)
    env = AgentIndicatorV1(parallel_to_aec(IndicatorEnv(space, observation)))
    env.reset()

    for index, agent in enumerate(AGENTS):
        transformed = env.observe(agent)
        assert transformed is not None

        original = observation if len(shape) != 2 else observation[..., None]
        np.testing.assert_array_equal(transformed[..., : original.shape[-1]], original)
        expected_indicator = np.zeros(transformed[..., original.shape[-1] :].shape)
        expected_indicator[..., index] = 2
        np.testing.assert_array_equal(
            transformed[..., original.shape[-1] :], expected_indicator
        )
        assert env.observation_space(agent).contains(transformed)


def test_aec_discrete_agent_indicators() -> None:
    space = gymnasium.spaces.Discrete(4, start=2)
    env = AgentIndicatorV1(parallel_to_aec(IndicatorEnv(space, np.array(4))))
    env.reset()

    for index, agent in enumerate(AGENTS):
        observation = env.observe(agent)
        assert observation == 2 * len(AGENTS) + index
        assert env.observation_space(agent).contains(observation)


def test_unbounded_box_uses_finite_indicators() -> None:
    space = gymnasium.spaces.Box(low=-np.inf, high=np.inf, shape=(1,), dtype=np.float32)
    env = AgentIndicatorParallelV1(IndicatorEnv(space, np.zeros(1, dtype=np.float32)))
    observations, _ = env.reset()

    for index, agent in enumerate(AGENTS):
        expected = np.zeros(1 + len(AGENTS), dtype=np.float32)
        expected[1 + index] = 1
        np.testing.assert_array_equal(observations[agent], expected)
        assert env.observation_space(agent).contains(expected)


def test_parallel_type_indicators_on_reset_and_step() -> None:
    space = gymnasium.spaces.Box(low=0, high=1, shape=(1,), dtype=np.float32)
    env = AgentIndicatorParallelV1(
        IndicatorEnv(space, np.zeros(1, dtype=np.float32)), type_only=True
    )

    reset_observations, _ = env.reset()
    step_observations, *_ = env.step(dict.fromkeys(env.agents, 0))

    reset_expected = {
        "predator_0": np.array([0, 1, 0], dtype=np.float32),
        "predator_1": np.array([0, 1, 0], dtype=np.float32),
        "prey_0": np.array([0, 0, 1], dtype=np.float32),
    }
    for agent in AGENTS:
        step_expected = reset_expected[agent].copy()
        step_expected[0] = 1
        np.testing.assert_array_equal(reset_observations[agent], reset_expected[agent])
        np.testing.assert_array_equal(step_observations[agent], step_expected)
        assert env.observation_space(agent).contains(step_expected)


def test_type_only_rejects_agent_names_with_a_suffix() -> None:
    env = IndicatorEnv(
        gymnasium.spaces.Box(low=0, high=1, shape=(1,), dtype=np.float32),
        np.zeros(1, dtype=np.float32),
    )
    env.possible_agents = ["predator_0", "predator_0_suffix"]

    with pytest.raises(
        AssertionError,
        match="agent names must follow the <type>_<n> format",
    ):
        AgentIndicatorParallelV1(env, type_only=True)


def test_rejects_non_homogeneous_observation_spaces() -> None:
    env = IndicatorEnv(
        gymnasium.spaces.Box(low=0, high=1, shape=(1,), dtype=np.float32),
        np.zeros(1, dtype=np.float32),
    )
    env.observation_space = lambda agent: gymnasium.spaces.Box(
        low=0,
        high=1,
        shape=(1 if agent == AGENTS[0] else 2,),
        dtype=np.float32,
    )

    with pytest.raises(AssertionError, match="observation spaces must be identical"):
        AgentIndicatorParallelV1(env)


@pytest.mark.parametrize("api", ["aec", "parallel"])
@pytest.mark.parametrize("shape", [(1024,), (32, 32), (16, 16, 4)])
@pytest.mark.parametrize("bound", ["low", "high"])
@pytest.mark.parametrize("close", [False, True])
def test_rejects_box_bounds_hidden_by_array_truncation(api, shape, bound, close):
    low = np.zeros(shape, dtype=np.float32)
    high = np.ones(shape, dtype=np.float32)
    low.flat[low.size // 2] = -2
    high.flat[high.size // 2] = 2
    first = gymnasium.spaces.Box(low=low, high=high, dtype=np.float32)
    changed = low.copy() if bound == "low" else high.copy()
    direction = -np.inf if bound == "low" else np.inf
    changed.flat[changed.size // 2] = (
        np.nextafter(changed.flat[changed.size // 2], direction, dtype=np.float32)
        if close
        else (-3 if bound == "low" else 3)
    )
    second = gymnasium.spaces.Box(
        low=changed if bound == "low" else low,
        high=changed if bound == "high" else high,
        dtype=np.float32,
    )
    env = IndicatorEnv(first, high)
    env.observation_space = lambda agent: first if agent == AGENTS[0] else second

    with np.printoptions(threshold=1000):
        assert repr(first) == repr(second)
        if close:
            # Box equality allows rounding tolerance; the returned bounds must
            # also contain observations exactly on either agent's endpoint.
            assert first == second
        wrapper = AgentIndicatorParallelV1
        if api == "aec":
            env = parallel_to_aec(env)
            wrapper = AgentIndicatorV1
        with pytest.raises(
            AssertionError, match="observation spaces must be identical"
        ):
            wrapper(env)


@pytest.mark.parametrize("api", ["aec", "parallel"])
@pytest.mark.parametrize("shape", [(1024,), (32, 32), (16, 16, 4)])
def test_accepts_separate_boxes_with_identical_bounds(api, shape):
    low = np.zeros(shape, dtype=np.float32)
    high = np.ones(shape, dtype=np.float32)
    low.flat[low.size // 2] = -2
    high.flat[high.size // 2] = 2
    first = gymnasium.spaces.Box(low=low, high=high, dtype=np.float32)
    env = IndicatorEnv(first, high)
    env.observation_space = lambda agent: gymnasium.spaces.Box(
        low=low.copy(), high=high.copy(), dtype=np.float32
    )
    if api == "aec":
        wrapped = AgentIndicatorV1(parallel_to_aec(env))
        wrapped.reset()
        observations = {agent: wrapped.observe(agent) for agent in AGENTS}
    else:
        wrapped = AgentIndicatorParallelV1(env)
        observations, _ = wrapped.reset()
    for agent, observation in observations.items():
        assert wrapped.observation_space(agent).contains(observation)
