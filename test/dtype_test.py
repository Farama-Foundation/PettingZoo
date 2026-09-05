from __future__ import annotations

import functools

import numpy as np
import pytest
from gymnasium.spaces import Box, Discrete

from pettingzoo.test import api_test, parallel_api_test
from pettingzoo.utils.env import AECEnv, ParallelEnv
from pettingzoo.utils.wrappers import DtypeObservationParallelV1, DtypeObservationV1

AGENTS = ["agent_0", "agent_1"]

FIXED_OBS = {
    "agent_0": np.arange(12, dtype=np.uint8).reshape(2, 2, 3),
    "agent_1": np.array([-1.0, -0.5, 0.25, 1.0], dtype=np.float32),
}


@functools.cache
def obs_space(agent):
    if agent == "agent_0":
        return Box(low=0, high=255, shape=(2, 2, 3), dtype=np.uint8)
    return Box(low=-1.0, high=1.0, shape=(4,), dtype=np.float32)


class DummyAEC(AECEnv):
    metadata = {"render_modes": [], "name": "dummy_aec"}

    def __init__(self):
        super().__init__()
        self.possible_agents = list(AGENTS)

    def observation_space(self, agent):
        return obs_space(agent)

    @functools.cache
    def action_space(self, agent):
        return Discrete(2)

    def reset(self, seed=None, options=None):
        self.agents = list(self.possible_agents)
        self.rewards = dict.fromkeys(self.agents, 0.0)
        self._cumulative_rewards = dict.fromkeys(self.agents, 0.0)
        self.terminations = dict.fromkeys(self.agents, False)
        self.truncations = dict.fromkeys(self.agents, False)
        self.infos = {a: {} for a in self.agents}
        self._idx = 0
        self._step_count = 0
        self.agent_selection = self.agents[0]

    def observe(self, agent):
        return FIXED_OBS[agent]

    def step(self, action):
        if (
            self.terminations[self.agent_selection]
            or self.truncations[self.agent_selection]
        ):
            self._was_dead_step(action)
            return
        self._step_count += 1
        self._cumulative_rewards[self.agent_selection] = 0.0
        self.rewards = dict.fromkeys(self.agents, 0.0)
        if self._step_count >= 8:
            self.terminations = dict.fromkeys(self.agents, True)
        self._idx = (self._idx + 1) % len(self.agents)
        self.agent_selection = self.agents[self._idx]
        self._accumulate_rewards()

    def render(self):
        return None

    def close(self):
        pass


class DummyParallel(ParallelEnv):
    metadata = {"render_modes": [], "name": "dummy_parallel"}

    def __init__(self):
        super().__init__()
        self.possible_agents = list(AGENTS)

    def observation_space(self, agent):
        return obs_space(agent)

    @functools.cache
    def action_space(self, agent):
        return Discrete(2)

    def reset(self, seed=None, options=None):
        self.agents = list(self.possible_agents)
        self._step_count = 0
        return dict(FIXED_OBS), {a: {} for a in self.agents}

    def step(self, actions):
        self._step_count += 1
        done = self._step_count >= 8
        obs = dict(FIXED_OBS)
        rewards = dict.fromkeys(self.agents, 0.0)
        terminations = dict.fromkeys(self.agents, done)
        truncations = dict.fromkeys(self.agents, False)
        infos = {a: {} for a in self.agents}
        if done:
            self.agents = []
        return obs, rewards, terminations, truncations, infos

    def render(self):
        return None

    def close(self):
        pass


class WideAEC(DummyAEC):
    """One agent, bounds and values that do not fit in a uint8."""

    def observation_space(self, agent):
        return Box(low=0.0, high=300.0, shape=(2,), dtype=np.float32)

    def observe(self, agent):
        return np.array([1.0, 300.0], dtype=np.float32)


class WideParallel(DummyParallel):
    def observation_space(self, agent):
        return Box(low=0.0, high=300.0, shape=(2,), dtype=np.float32)

    def reset(self, seed=None, options=None):
        self.agents = list(self.possible_agents)
        self._step_count = 0
        obs = dict.fromkeys(self.agents, np.array([1.0, 300.0], dtype=np.float32))
        return obs, {a: {} for a in self.agents}


class UnboundedAEC(DummyAEC):
    def observation_space(self, agent):
        return Box(low=-np.inf, high=np.inf, shape=(2,), dtype=np.float32)

    def observe(self, agent):
        return np.array([1.5, -2.5], dtype=np.float32)


# shape, low, high each agent's space should have after a cast to float32.
EXPECTED_FLOAT32 = {
    "agent_0": ((2, 2, 3), 0.0, 255.0),
    "agent_1": ((4,), -1.0, 1.0),
}


@pytest.mark.parametrize("agent", AGENTS)
def test_aec_observation_space(agent):
    space = DtypeObservationV1(DummyAEC(), np.float32).observation_space(agent)
    shape, low, high = EXPECTED_FLOAT32[agent]
    assert isinstance(space, Box)
    assert space.dtype == np.float32
    assert space.shape == shape
    assert (space.low == low).all()
    assert (space.high == high).all()


@pytest.mark.parametrize("agent", AGENTS)
def test_parallel_observation_space(agent):
    space = DtypeObservationParallelV1(DummyParallel(), np.float32).observation_space(
        agent
    )
    shape, low, high = EXPECTED_FLOAT32[agent]
    assert isinstance(space, Box)
    assert space.dtype == np.float32
    assert space.shape == shape
    assert (space.low == low).all()
    assert (space.high == high).all()


@pytest.mark.parametrize("agent", AGENTS)
def test_aec_observe_is_cast(agent):
    env = DtypeObservationV1(DummyAEC(), np.float32)
    env.reset(seed=0)

    obs = env.observe(agent)
    assert obs.dtype == np.float32
    assert np.array_equal(obs, FIXED_OBS[agent].astype(np.float32))
    assert env.observation_space(agent).contains(obs)


@pytest.mark.parametrize("agent", AGENTS)
def test_parallel_reset_and_step_are_cast(agent):
    env = DtypeObservationParallelV1(DummyParallel(), np.float32)

    obs, _ = env.reset(seed=0)
    assert obs[agent].dtype == np.float32
    assert np.array_equal(obs[agent], FIXED_OBS[agent].astype(np.float32))
    assert env.observation_space(agent).contains(obs[agent])

    obs, _, _, _, _ = env.step(dict.fromkeys(env.agents, 0))
    assert obs[agent].dtype == np.float32
    assert np.array_equal(obs[agent], FIXED_OBS[agent].astype(np.float32))


@pytest.mark.parametrize("agent", AGENTS)
def test_aec_last_is_cast(agent):
    env = DtypeObservationV1(DummyAEC(), np.float32)
    env.reset(seed=0)
    while env.agent_selection != agent:
        env.step(0)

    obs, _, _, _, _ = env.last()
    assert obs.dtype == np.float32
    assert np.array_equal(obs, FIXED_OBS[agent].astype(np.float32))


def test_uint8_image_to_float32():
    env = DtypeObservationV1(DummyAEC(), np.float32)
    env.reset(seed=0)

    space = env.observation_space("agent_0")
    assert space.shape == (2, 2, 3)
    assert (space.low == 0.0).all()
    assert (space.high == 255.0).all()

    obs = env.observe("agent_0")
    assert obs.dtype == np.float32
    assert np.array_equal(obs, np.arange(12, dtype=np.float32).reshape(2, 2, 3))


def test_downcast_wraps_bounds_like_supersuit():
    """A cast that overflows the new dtype wraps, in the space and the value."""
    env = DtypeObservationV1(WideAEC(), np.uint8)
    env.reset(seed=0)

    space = env.observation_space("agent_0")
    assert space.dtype == np.uint8
    assert np.array_equal(space.low, np.array([0, 0], dtype=np.uint8))
    assert np.array_equal(space.high, np.array([44, 44], dtype=np.uint8))  # 300 % 256

    obs = env.observe("agent_0")
    assert obs.dtype == np.uint8
    assert np.array_equal(obs, np.array([1, 44], dtype=np.uint8))


def test_parallel_downcast_wraps_bounds_like_supersuit():
    env = DtypeObservationParallelV1(WideParallel(), np.uint8)

    space = env.observation_space("agent_0")
    assert space.dtype == np.uint8
    assert np.array_equal(space.low, np.array([0, 0], dtype=np.uint8))
    assert np.array_equal(space.high, np.array([44, 44], dtype=np.uint8))

    obs, _ = env.reset(seed=0)
    assert obs["agent_0"].dtype == np.uint8
    assert np.array_equal(obs["agent_0"], np.array([1, 44], dtype=np.uint8))


def test_unbounded_space_cast_to_int_collapses():
    """Casting an infinite bound to an int dtype is undefined, as in SuperSuit."""
    with pytest.warns(RuntimeWarning, match="invalid value encountered in cast"):
        env = DtypeObservationV1(UnboundedAEC(), np.int32)

    space = env.observation_space("agent_0")
    assert space.dtype == np.int32
    assert np.array_equal(space.low, np.array([np.iinfo(np.int32).min] * 2))
    assert np.array_equal(space.high, np.array([np.iinfo(np.int32).min] * 2))

    env.reset(seed=0)
    assert not space.contains(env.observe("agent_0"))
    with pytest.raises(AssertionError, match="Out of bounds observation"):
        api_test(env, num_cycles=2)


def test_impossible_cast_names_the_wrapper_and_agent():
    with pytest.raises(
        ValueError, match=r"DtypeObservationV1 cannot cast agent 'agent_0'"
    ):
        DtypeObservationV1(DummyAEC(), np.int8)

    with pytest.raises(
        ValueError, match=r"DtypeObservationParallelV1 cannot cast agent 'agent_0'"
    ):
        DtypeObservationParallelV1(DummyParallel(), np.int8)


def test_str():
    inner = DummyAEC()
    assert (
        str(DtypeObservationV1(inner, np.float32)) == f"DtypeObservationV1<{inner!s}>"
    )
    inner = DummyParallel()
    assert (
        str(DtypeObservationParallelV1(inner, np.float32))
        == f"DtypeObservationParallelV1<{inner!s}>"
    )


def test_observe_passes_through_none():
    class NoneObsEnv(DummyAEC):
        def observe(self, agent):
            return None

    env = DtypeObservationV1(NoneObsEnv(), np.float32)
    env.reset(seed=0)
    assert env.observe("agent_0") is None


def test_aec_api():
    api_test(DtypeObservationV1(DummyAEC(), np.float32), num_cycles=5)


def test_parallel_api():
    parallel_api_test(
        DtypeObservationParallelV1(DummyParallel(), np.float32), num_cycles=5
    )


def test_rejects_parallel_env():
    with pytest.raises(AssertionError):
        DtypeObservationV1(DummyParallel(), np.float32)


def test_rejects_bad_dtype():
    with pytest.raises(TypeError):
        DtypeObservationV1(DummyAEC(), "not_a_dtype")


def test_rejects_non_box_space_at_construction():
    class DiscreteObsAEC(DummyAEC):
        def observation_space(self, agent):
            return Discrete(4)

    class DiscreteObsParallel(DummyParallel):
        def observation_space(self, agent):
            return Discrete(4)

    with pytest.raises(
        AssertionError, match="DtypeObservationV1 only supports Box observation spaces"
    ):
        DtypeObservationV1(DiscreteObsAEC(), np.float32)

    with pytest.raises(
        AssertionError,
        match="DtypeObservationParallelV1 only supports Box observation spaces",
    ):
        DtypeObservationParallelV1(DiscreteObsParallel(), np.float32)


def test_agent_outside_possible_agents_resolves_lazily():
    class ExtraAgentEnv(DummyAEC):
        def observation_space(self, agent):
            if agent == "agent_2":
                return Box(low=0.0, high=1.0, shape=(3,), dtype=np.float64)
            return obs_space(agent)

    env = DtypeObservationV1(ExtraAgentEnv(), np.float32)
    space = env.observation_space("agent_2")
    assert space.dtype == np.float32
    assert space.shape == (3,)
