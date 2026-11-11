"""Black-death placeholders must belong to each agent's observation space."""

from __future__ import annotations

import numpy as np
import pytest
from gymnasium.spaces import Box

from pettingzoo.test import parallel_api_test
from pettingzoo.utils.wrappers import (
    BlackDeathParallelV4,
    DtypeObservationParallelV1,
)
from test.black_death_test import AGENTS, EarlyDepartureParallel


class BoundedDeparture(EarlyDepartureParallel):
    """An early-departure environment with per-agent Box bounds."""

    def __init__(self, departing_space: Box):
        super().__init__()
        self.spaces = {
            AGENTS[0]: departing_space,
            AGENTS[1]: Box(2, 4, shape=(2,), dtype=np.float32),
            AGENTS[2]: Box(-4, -2, shape=(2,), dtype=np.float32),
        }

    def observation_space(self, agent):
        return self.spaces[agent]

    def _observation(self, agent):
        space = self.observation_space(agent)
        return np.asarray(
            np.clip(np.zeros(space.shape, dtype=space.dtype), space.low, space.high),
            dtype=space.dtype,
        )


@pytest.mark.parametrize(
    "space",
    [
        Box(1, 3, shape=(2,), dtype=np.float32),
        Box(-3, -1, shape=(2,), dtype=np.float64),
        Box(np.array([1, -3]), np.array([3, -1]), dtype=np.float32),
        Box(1, 3, shape=(2,), dtype=np.int8),
        Box(1, 3, shape=(2,), dtype=np.uint8),
        Box(1, 3, shape=(), dtype=np.float32),
        Box(-1, 1, shape=(2,), dtype=np.float32),
        Box(-np.inf, np.inf, shape=(2,), dtype=np.float32),
    ],
)
def test_zero_placeholders_belong_to_advertised_space(space):
    """Original and placeholder observations fit without mutating source bounds."""
    inner = BoundedDeparture(space)
    original_low, original_high = space.low.copy(), space.high.copy()
    env = BlackDeathParallelV4(inner)
    observations, _ = env.reset()
    for agent, obs in observations.items():
        assert env.observation_space(agent).contains(obs)
        assert inner.observation_space(agent).contains(obs)

    env.step(dict.fromkeys(AGENTS, 0))
    observations, rewards, terminations, truncations, infos = env.step(
        dict.fromkeys(AGENTS, 0)
    )

    placeholder = observations[AGENTS[0]]
    np.testing.assert_array_equal(placeholder, np.zeros(space.shape, dtype=space.dtype))
    assert placeholder.dtype == space.dtype
    assert env.observation_space(AGENTS[0]).contains(placeholder)
    for agent, obs in observations.items():
        assert env.observation_space(agent).contains(obs)

    advertised = env.observation_space(AGENTS[0])
    assert advertised is env.observation_space(AGENTS[0])
    np.testing.assert_array_equal(advertised.low, np.minimum(original_low, 0))
    np.testing.assert_array_equal(advertised.high, np.maximum(original_high, 0))
    np.testing.assert_array_equal(space.low, original_low)
    np.testing.assert_array_equal(space.high, original_high)
    assert rewards[AGENTS[0]] == 0
    assert infos[AGENTS[0]] == {}
    assert terminations == dict.fromkeys(AGENTS, True)
    assert truncations == dict.fromkeys(AGENTS, False)


def test_space_containing_zero_is_preserved():
    """Already-compatible spaces retain their identity and generator state."""
    space = Box(-1, 1, shape=(2,), dtype=np.float32, seed=123)
    expected = Box(-1, 1, shape=(2,), dtype=np.float32, seed=123).sample()
    env = BlackDeathParallelV4(BoundedDeparture(space))
    assert env.observation_space(AGENTS[0]) is space
    env.reset()
    assert env.observation_space(AGENTS[0]) is space
    np.testing.assert_array_equal(space.sample(), expected)


def test_widened_space_survives_reset_with_its_seed():
    """Reset does not discard a widened space that the caller already seeded."""
    source = Box(1, 3, shape=(2,), dtype=np.float32)
    env = BlackDeathParallelV4(BoundedDeparture(source))
    advertised = env.observation_space(AGENTS[0])
    advertised.seed(42)
    expected = Box(0, 3, shape=(2,), dtype=np.float32, seed=42).sample()

    env.reset()
    assert env.observation_space(AGENTS[0]) is advertised
    np.testing.assert_array_equal(advertised.sample(), expected)


def test_bounds_refresh_when_agent_spaces_change_on_reset():
    """Reused agent IDs can acquire a different space in a later episode."""
    inner = BoundedDeparture(Box(1, 3, shape=(2,), dtype=np.float32))
    env = BlackDeathParallelV4(inner)
    env.reset()
    previous = env.observation_space(AGENTS[0])

    inner.spaces[AGENTS[0]] = Box(-5, -2, shape=(3,), dtype=np.float64)
    observations, _ = env.reset(seed=4, options={"new_episode": True})
    refreshed = env.observation_space(AGENTS[0])

    assert refreshed is not previous
    assert refreshed.shape == (3,)
    assert refreshed.dtype == np.float64
    np.testing.assert_array_equal(refreshed.low, [-5, -5, -5])
    np.testing.assert_array_equal(refreshed.high, [0, 0, 0])
    assert refreshed.contains(observations[AGENTS[0]])
    env.step(dict.fromkeys(AGENTS, 0))
    observations, *_ = env.step(dict.fromkeys(AGENTS, 0))
    assert refreshed.contains(observations[AGENTS[0]])


def test_placeholder_remains_valid_after_dtype_conversion():
    """Downstream wrappers inherit bounds that include the zero placeholder."""
    inner = BoundedDeparture(Box(1, 3, shape=(2,), dtype=np.float32))
    env = DtypeObservationParallelV1(BlackDeathParallelV4(inner), np.float64)
    env.reset()
    env.step(dict.fromkeys(AGENTS, 0))
    observations, *_ = env.step(dict.fromkeys(AGENTS, 0))

    for agent, obs in observations.items():
        assert obs.dtype == np.float64
        assert env.observation_space(agent).contains(obs)
    np.testing.assert_array_equal(observations[AGENTS[0]], [0, 0])


def test_positive_bounds_parallel_api():
    """The native wrapper still obeys the Parallel API with widened bounds."""
    parallel_api_test(
        BlackDeathParallelV4(BoundedDeparture(Box(1, 3, shape=(2,), dtype=np.float32))),
        num_cycles=3,
    )
