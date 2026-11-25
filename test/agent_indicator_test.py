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


@pytest.mark.parametrize("aec", [False, True], ids=["parallel", "aec"])
@pytest.mark.parametrize("bound", ["low", "high"])
@pytest.mark.parametrize("difference", [0.25, 1e-6], ids=["large", "within-allclose"])
def test_rejects_bounds_hidden_by_array_representation(aec, bound, difference) -> None:
    """Space validation must see bounds omitted from NumPy's printed arrays."""
    low = np.ones(1024, dtype=np.float32)
    low[0] = -1
    high = np.full(1024, 3, dtype=np.float32)
    high[0] = 4
    first = gymnasium.spaces.Box(low=low, high=high, dtype=np.float32)
    other_low, other_high = low.copy(), high.copy()
    (other_low if bound == "low" else other_high)[512] += difference
    other = gymnasium.spaces.Box(low=other_low, high=other_high, dtype=np.float32)
    env = IndicatorEnv(first, np.full(1024, 2, dtype=np.float32))
    env.observation_space = lambda agent: first if agent == AGENTS[0] else other
    wrapped = parallel_to_aec(env) if aec else env
    wrapper = AgentIndicatorV1 if aec else AgentIndicatorParallelV1

    with np.printoptions(threshold=1000):
        assert repr(first) == repr(other)
        assert not np.array_equal(getattr(first, bound), getattr(other, bound))
        with pytest.raises(
            AssertionError, match="observation spaces must be identical"
        ):
            wrapper(wrapped)


@pytest.mark.parametrize("aec", [False, True], ids=["parallel", "aec"])
@pytest.mark.parametrize("dtype", [np.float32, np.float64])
def test_accepts_distinct_boxes_with_identical_bounds(aec, dtype) -> None:
    """Equivalent separate Box objects still produce valid indicated observations."""
    low = np.array([-1, 0, 1], dtype=dtype)
    high = np.array([1, 2, 3], dtype=dtype)
    spaces = {
        agent: gymnasium.spaces.Box(low=low.copy(), high=high.copy(), dtype=dtype)
        for agent in AGENTS
    }
    env = IndicatorEnv(spaces[AGENTS[0]], np.array([0, 1, 2], dtype=dtype))
    env.observation_space = lambda agent: spaces[agent]

    if aec:
        indicated = AgentIndicatorV1(parallel_to_aec(env))
        indicated.reset()
        observations = {agent: indicated.observe(agent) for agent in AGENTS}
    else:
        indicated = AgentIndicatorParallelV1(env)
        observations, _ = indicated.reset()

    for index, agent in enumerate(AGENTS):
        expected = np.array([0, 1, 2] + [0] * len(AGENTS), dtype=dtype)
        expected[3 + index] = 3
        np.testing.assert_array_equal(observations[agent], expected)
        assert indicated.observation_space(agent).contains(observations[agent])


@pytest.mark.parametrize("aec", [False, True], ids=["parallel", "aec"])
def test_accepts_distinct_equivalent_discrete_spaces(aec) -> None:
    """Separate Discrete spaces retain the existing start-offset mapping."""
    spaces = {agent: gymnasium.spaces.Discrete(4, start=2) for agent in AGENTS}
    env = IndicatorEnv(spaces[AGENTS[0]], np.array(4))
    env.observation_space = lambda agent: spaces[agent]

    if aec:
        indicated = AgentIndicatorV1(parallel_to_aec(env))
        indicated.reset()
        observations = {agent: indicated.observe(agent) for agent in AGENTS}
    else:
        indicated = AgentIndicatorParallelV1(env)
        observations, _ = indicated.reset()

    for index, agent in enumerate(AGENTS):
        assert observations[agent] == 2 * len(AGENTS) + index
        assert indicated.observation_space(agent).contains(observations[agent])
