from __future__ import annotations

from typing import Any

import gymnasium.spaces
import numpy as np
import pytest

from pettingzoo.utils.conversions import parallel_to_aec
from pettingzoo.utils.env import ParallelEnv
from pettingzoo.utils.wrappers import AgentIndicator, AgentIndicatorParallel

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
    env = AgentIndicator(parallel_to_aec(IndicatorEnv(space, observation)))
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
    env = AgentIndicator(parallel_to_aec(IndicatorEnv(space, np.array(4))))
    env.reset()

    for index, agent in enumerate(AGENTS):
        observation = env.observe(agent)
        assert observation == 2 * len(AGENTS) + index
        assert env.observation_space(agent).contains(observation)


def test_unbounded_box_uses_finite_indicators() -> None:
    space = gymnasium.spaces.Box(low=-np.inf, high=np.inf, shape=(1,), dtype=np.float32)
    env = AgentIndicatorParallel(IndicatorEnv(space, np.zeros(1, dtype=np.float32)))
    observations, _ = env.reset()

    for index, agent in enumerate(AGENTS):
        expected = np.zeros(1 + len(AGENTS), dtype=np.float32)
        expected[1 + index] = 1
        np.testing.assert_array_equal(observations[agent], expected)
        assert env.observation_space(agent).contains(expected)


def test_parallel_type_indicators_on_reset_and_step() -> None:
    space = gymnasium.spaces.Box(low=0, high=1, shape=(1,), dtype=np.float32)
    env = AgentIndicatorParallel(
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
        AgentIndicatorParallel(env)
