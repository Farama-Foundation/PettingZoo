from __future__ import annotations

import functools

import numpy as np
import pytest
from gymnasium.spaces import Box, Discrete

from pettingzoo.test import api_test, parallel_api_test
from pettingzoo.utils.env import AECEnv, ParallelEnv
from pettingzoo.utils.wrappers import RescaleObservationParallelV1, RescaleObservationV1

AGENTS = ["agent_0", "agent_1"]

# (0.0, 1.0) is the one range where the float32 arithmetic happens to be exact.
RANGES = [(0.0, 1.0), (0.1, 0.7), (-2.0, 4.0)]

# agent_0 has scalar bounds, agent_1 has a different [low, high] per element.
SPACES = {
    "agent_0": Box(low=-1.0, high=3.0, shape=(2,), dtype=np.float32),
    "agent_1": Box(
        low=np.array([0.0, -10.0, 2.0], dtype=np.float32),
        high=np.array([1.0, 10.0, 6.0], dtype=np.float32),
        dtype=np.float32,
    ),
}

FIXED_OBS = {
    "agent_0": np.array([1.0, -1.0], dtype=np.float32),
    "agent_1": np.array([0.25, 0.0, 6.0], dtype=np.float32),
}

# Hand computed: (obs - low) / (high - low).
UNIT_OBS = {
    "agent_0": np.array([0.5, 0.0], dtype=np.float32),
    "agent_1": np.array([0.25, 0.5, 1.0], dtype=np.float32),
}


@functools.cache
def obs_space(agent):
    return SPACES[agent]


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


def aec_with_space(space, obs=None):
    class FixedSpaceAEC(DummyAEC):
        def observation_space(self, agent):
            return space

        def observe(self, agent):
            return FIXED_OBS[agent] if obs is None else obs

    return FixedSpaceAEC()


@pytest.mark.parametrize("agent", AGENTS)
def test_aec_observation_space(agent):
    space = RescaleObservationV1(DummyAEC(), -2.0, 4.0).observation_space(agent)
    assert isinstance(space, Box)
    assert space.shape == SPACES[agent].shape
    assert space.dtype == SPACES[agent].dtype
    assert np.all(space.low == -2.0)
    assert np.all(space.high == 4.0)


@pytest.mark.parametrize("agent", AGENTS)
def test_parallel_observation_space(agent):
    space = RescaleObservationParallelV1(DummyParallel(), -2.0, 4.0).observation_space(
        agent
    )
    assert isinstance(space, Box)
    assert space.shape == SPACES[agent].shape
    assert space.dtype == SPACES[agent].dtype
    assert np.all(space.low == -2.0)
    assert np.all(space.high == 4.0)


@pytest.mark.parametrize("agent", AGENTS)
def test_aec_observe_matches_expected(agent):
    env = RescaleObservationV1(DummyAEC())
    env.reset(seed=0)
    obs = env.observe(agent)
    assert np.allclose(obs, UNIT_OBS[agent])
    assert obs.dtype == SPACES[agent].dtype
    assert env.observation_space(agent).contains(obs)


@pytest.mark.parametrize("agent", AGENTS)
def test_parallel_reset_and_step_match_expected(agent):
    env = RescaleObservationParallelV1(DummyParallel())
    obs, _ = env.reset(seed=0)
    assert np.allclose(obs[agent], UNIT_OBS[agent])
    assert env.observation_space(agent).contains(obs[agent])

    obs, _, _, _, _ = env.step(dict.fromkeys(env.agents, 0))
    assert np.allclose(obs[agent], UNIT_OBS[agent])
    assert env.observation_space(agent).contains(obs[agent])


@pytest.mark.parametrize("agent", AGENTS)
def test_aec_last_matches_expected(agent):
    env = RescaleObservationV1(DummyAEC())
    env.reset(seed=0)
    while env.agent_selection != agent:
        env.step(0)

    obs, _, _, _, _ = env.last()
    assert np.allclose(obs, UNIT_OBS[agent])


@pytest.mark.parametrize("min_obs, max_obs", [(0.0, 1.0), (-2.0, 4.0), (-1.0, -0.5)])
def test_midpoint_lands_in_the_middle(min_obs, max_obs):
    # agent_0's first element sits exactly halfway through [-1, 3].
    env = RescaleObservationV1(DummyAEC(), min_obs, max_obs)
    env.reset(seed=0)
    obs = env.observe("agent_0")
    assert obs[0] == pytest.approx((min_obs + max_obs) / 2)
    assert obs[1] == pytest.approx(min_obs)


def test_float64_space_keeps_its_dtype():
    space = Box(low=-1.0, high=3.0, shape=(2,), dtype=np.float64)
    env = RescaleObservationV1(aec_with_space(space))
    env.reset(seed=0)
    obs = env.observe("agent_0")
    assert env.observation_space("agent_0").dtype == np.float64
    assert obs.dtype == np.float64
    assert np.allclose(obs, UNIT_OBS["agent_0"])


def test_observe_passes_through_none():
    class NoneObsEnv(DummyAEC):
        def observe(self, agent):
            return None

    env = RescaleObservationV1(NoneObsEnv())
    env.reset(seed=0)
    assert env.observe("agent_0") is None


class OneAgentAEC(DummyAEC):
    def __init__(self):
        super().__init__()
        self.possible_agents = ["agent_0"]


def test_agent_outside_possible_agents_resolves_lazily():
    env = RescaleObservationV1(OneAgentAEC(), -2.0, 4.0)
    space = env.observation_space("agent_1")
    assert space.shape == SPACES["agent_1"].shape
    assert np.all(space.low == -2.0)
    assert np.all(space.high == 4.0)


def test_agent_outside_possible_agents_still_checks_its_space():
    class LateBadSpaceAEC(OneAgentAEC):
        def observation_space(self, agent):
            return Discrete(3) if agent == "agent_1" else obs_space(agent)

    env = RescaleObservationV1(LateBadSpaceAEC())
    with pytest.raises(AssertionError, match="Box observation spaces"):
        env.observation_space("agent_1")


def test_rejects_zero_width_element():
    space = Box(
        low=np.array([0.0, 5.0], dtype=np.float32),
        high=np.array([1.0, 5.0], dtype=np.float32),
        dtype=np.float32,
    )
    with pytest.raises(AssertionError, match="high > low"):
        RescaleObservationV1(aec_with_space(space))


def test_wide_float32_space_does_not_overflow():
    # high - low overflows to inf in float32, which used to give NaN or min_obs.
    space = Box(low=-2e38, high=2e38, shape=(2,), dtype=np.float32)
    obs = np.array([2e38, 0.0], dtype=np.float32)
    env = RescaleObservationV1(aec_with_space(space, obs))
    env.reset(seed=0)

    got = env.observe("agent_0")
    assert not np.any(np.isnan(got))
    assert np.allclose(got, [1.0, 0.5])
    assert env.observation_space("agent_0").contains(got)


def test_rejects_integer_space():
    space = Box(low=0, high=255, shape=(2,), dtype=np.uint8)
    with pytest.raises(AssertionError, match="float32 or float64"):
        RescaleObservationV1(aec_with_space(space))


def test_rejects_non_box_space():
    with pytest.raises(AssertionError, match="Box observation spaces"):
        RescaleObservationV1(aec_with_space(Discrete(3)))


def test_rejects_unbounded_space():
    space = Box(low=-np.inf, high=np.inf, shape=(2,), dtype=np.float32)
    with pytest.raises(AssertionError, match="infinite bounds"):
        RescaleObservationV1(aec_with_space(space))


@pytest.mark.parametrize("min_obs, max_obs", [(1.0, 1.0), (1.0, 0.0)])
def test_rejects_bad_range(min_obs, max_obs):
    with pytest.raises(AssertionError, match="greater than min_obs"):
        RescaleObservationV1(DummyAEC(), min_obs, max_obs)
    with pytest.raises(AssertionError, match="greater than min_obs"):
        RescaleObservationParallelV1(DummyParallel(), min_obs, max_obs)


def test_rejects_parallel_env():
    with pytest.raises(AssertionError, match="use RescaleObservationParallelV1"):
        RescaleObservationV1(DummyParallel())


@pytest.mark.parametrize("agent", AGENTS)
@pytest.mark.parametrize("min_obs, max_obs", RANGES)
def test_aec_observation_stays_in_the_advertised_space(agent, min_obs, max_obs):
    env = RescaleObservationV1(DummyAEC(), min_obs, max_obs)
    env.reset(seed=0)
    obs = env.observe(agent)
    assert env.observation_space(agent).contains(obs)


@pytest.mark.parametrize("agent", AGENTS)
@pytest.mark.parametrize("min_obs, max_obs", RANGES)
def test_parallel_observation_stays_in_the_advertised_space(agent, min_obs, max_obs):
    env = RescaleObservationParallelV1(DummyParallel(), min_obs, max_obs)
    obs, _ = env.reset(seed=0)
    assert env.observation_space(agent).contains(obs[agent])

    obs, _, _, _, _ = env.step(dict.fromkeys(env.agents, 0))
    assert env.observation_space(agent).contains(obs[agent])


@pytest.mark.parametrize("min_obs, max_obs", RANGES)
def test_aec_api(min_obs, max_obs):
    api_test(RescaleObservationV1(DummyAEC(), min_obs, max_obs), num_cycles=5)


@pytest.mark.parametrize("min_obs, max_obs", RANGES)
def test_parallel_api(min_obs, max_obs):
    parallel_api_test(
        RescaleObservationParallelV1(DummyParallel(), min_obs, max_obs), num_cycles=5
    )
