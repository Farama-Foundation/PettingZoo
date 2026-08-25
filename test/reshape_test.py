from __future__ import annotations

import functools

import numpy as np
import pytest
from gymnasium.spaces import Box, Discrete

from pettingzoo.test import api_test, parallel_api_test
from pettingzoo.utils.env import AECEnv, ParallelEnv
from pettingzoo.utils.wrappers import ReshapeObservation, ReshapeObservationParallel

AGENTS = ["agent_0", "agent_1"]

NEW_SHAPE = (3, 2)

LOW_0 = np.arange(6, dtype=np.float32).reshape(2, 3)
HIGH_0 = LOW_0 + 1.0
LOW_1 = -np.arange(1, 7, dtype=np.float32)
HIGH_1 = -LOW_1

FIXED_OBS = {
    "agent_0": LOW_0 + 0.5,
    "agent_1": np.arange(6, dtype=np.float32) / 10.0,
}


@functools.cache
def obs_space(agent):
    if agent == "agent_0":
        return Box(low=LOW_0, high=HIGH_0, dtype=np.float32)
    return Box(low=LOW_1, high=HIGH_1, dtype=np.float32)


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


class Uint8AEC(DummyAEC):
    """An env whose observations are uint8, to check the dtype survives."""

    def observation_space(self, agent):
        return Box(low=0, high=255, shape=(2, 3), dtype=np.uint8)

    def observe(self, agent):
        return np.arange(6, dtype=np.uint8).reshape(2, 3)


class Uint8Parallel(DummyParallel):
    """An env whose observations are uint8, to check the dtype survives."""

    def observation_space(self, agent):
        return Box(low=0, high=255, shape=(2, 3), dtype=np.uint8)

    def reset(self, seed=None, options=None):
        self.agents = list(self.possible_agents)
        self._step_count = 0
        obs = {a: np.arange(6, dtype=np.uint8).reshape(2, 3) for a in self.agents}
        return obs, {a: {} for a in self.agents}


class LateAgentsAEC(DummyAEC):
    """An env that only fills possible_agents in reset, like the generated_agents envs."""

    def __init__(self):
        AECEnv.__init__(self)

    def reset(self, seed=None, options=None):
        self.possible_agents = list(AGENTS)
        super().reset(seed=seed, options=options)


class LateAgentsParallel(DummyParallel):
    """An env that only fills possible_agents in reset, like the generated_agents envs."""

    def __init__(self):
        ParallelEnv.__init__(self)

    def reset(self, seed=None, options=None):
        self.possible_agents = list(AGENTS)
        return super().reset(seed=seed, options=options)


@pytest.mark.parametrize("agent", AGENTS)
def test_aec_observation_space_has_new_shape(agent):
    space = ReshapeObservation(DummyAEC(), NEW_SHAPE).observation_space(agent)
    assert isinstance(space, Box)
    assert space.shape == NEW_SHAPE
    assert space.dtype == np.float32


@pytest.mark.parametrize("agent", AGENTS)
def test_parallel_observation_space_has_new_shape(agent):
    space = ReshapeObservationParallel(DummyParallel(), NEW_SHAPE).observation_space(
        agent
    )
    assert isinstance(space, Box)
    assert space.shape == NEW_SHAPE


@pytest.mark.parametrize(
    "wrapper,env",
    [(ReshapeObservation, DummyAEC), (ReshapeObservationParallel, DummyParallel)],
)
def test_per_element_bounds_are_reshaped_not_collapsed(wrapper, env):
    space = wrapper(env(), NEW_SHAPE).observation_space("agent_0")
    assert np.array_equal(space.low, LOW_0.reshape(NEW_SHAPE))
    assert np.array_equal(space.high, HIGH_0.reshape(NEW_SHAPE))
    assert len(np.unique(space.low)) == 6


def test_aec_keeps_dtype():
    env = ReshapeObservation(Uint8AEC(), NEW_SHAPE)
    env.reset(seed=0)
    space = env.observation_space("agent_0")
    assert space.dtype == np.uint8
    assert space.low.dtype == np.uint8
    assert space.high.max() == 255
    assert env.observe("agent_0").dtype == np.uint8


def test_parallel_keeps_dtype():
    env = ReshapeObservationParallel(Uint8Parallel(), NEW_SHAPE)
    obs, _ = env.reset(seed=0)
    assert env.observation_space("agent_0").dtype == np.uint8
    assert obs["agent_0"].dtype == np.uint8


@pytest.mark.parametrize("agent", AGENTS)
def test_aec_observe_matches_reshape(agent):
    env = ReshapeObservation(DummyAEC(), NEW_SHAPE)
    env.reset(seed=0)

    obs = env.observe(agent)
    assert obs.shape == NEW_SHAPE
    assert np.array_equal(obs, FIXED_OBS[agent].reshape(NEW_SHAPE))
    assert env.observation_space(agent).contains(obs)


@pytest.mark.parametrize("agent", AGENTS)
def test_parallel_reset_matches_reshape(agent):
    env = ReshapeObservationParallel(DummyParallel(), NEW_SHAPE)
    obs, _ = env.reset(seed=0)
    assert np.array_equal(obs[agent], FIXED_OBS[agent].reshape(NEW_SHAPE))
    assert env.observation_space(agent).contains(obs[agent])


@pytest.mark.parametrize("agent", AGENTS)
def test_parallel_step_matches_reshape(agent):
    env = ReshapeObservationParallel(DummyParallel(), NEW_SHAPE)
    env.reset(seed=0)
    obs, _, _, _, _ = env.step(dict.fromkeys(env.agents, 0))
    assert np.array_equal(obs[agent], FIXED_OBS[agent].reshape(NEW_SHAPE))


@pytest.mark.parametrize("agent", AGENTS)
def test_aec_last_matches_reshape(agent):
    env = ReshapeObservation(DummyAEC(), NEW_SHAPE)
    env.reset(seed=0)
    while env.agent_selection != agent:
        env.step(0)

    obs, _, _, _, _ = env.last()
    assert np.array_equal(obs, FIXED_OBS[agent].reshape(NEW_SHAPE))


def test_observe_passes_through_none():
    class NoneObsEnv(DummyAEC):
        def observe(self, agent):
            return None

    env = ReshapeObservation(NoneObsEnv(), NEW_SHAPE)
    env.reset(seed=0)
    assert env.observe("agent_0") is None


@pytest.mark.parametrize(
    "wrapper,env",
    [(ReshapeObservation, DummyAEC), (ReshapeObservationParallel, DummyParallel)],
)
def test_rejects_shape_with_wrong_number_of_elements(wrapper, env):
    with pytest.raises(AssertionError, match="as many elements"):
        wrapper(env(), (2, 2))


@pytest.mark.parametrize("shape", [6, [3, 2], (3.0, 2.0), (-1, 6), (-2, -3)])
def test_rejects_invalid_shapes(shape):
    with pytest.raises(AssertionError):
        ReshapeObservation(DummyAEC(), shape)


def test_rejects_empty_shape():
    with pytest.raises(AssertionError, match="must not be empty"):
        ReshapeObservation(DummyAEC(), ())


def test_minus_one_message_is_only_about_minus_one():
    with pytest.raises(AssertionError, match="-1 is not supported"):
        ReshapeObservation(DummyAEC(), (-1, 6))
    with pytest.raises(AssertionError, match="positive ints"):
        ReshapeObservation(DummyAEC(), (0, 6))


def test_bad_shape_is_caught_when_agents_appear_late():
    env = ReshapeObservation(LateAgentsAEC(), (5, 7))
    env.reset(seed=0)
    with pytest.raises(AssertionError, match="as many elements"):
        env.observe("agent_0")


def test_parallel_bad_shape_is_caught_when_agents_appear_late():
    env = ReshapeObservationParallel(LateAgentsParallel(), (5, 7))
    with pytest.raises(AssertionError, match="agent_0"):
        env.reset(seed=0)


def test_str():
    aec = DummyAEC()
    assert str(ReshapeObservation(aec, NEW_SHAPE)) == f"ReshapeObservation<{aec!s}>"
    par = DummyParallel()
    assert (
        str(ReshapeObservationParallel(par, NEW_SHAPE))
        == f"ReshapeObservationParallel<{par!s}>"
    )


def test_rejects_non_box_observation_space():
    class DiscreteObsEnv(DummyAEC):
        def observation_space(self, agent):
            return Discrete(6)

    with pytest.raises(AssertionError, match="Box observation spaces"):
        ReshapeObservation(DiscreteObsEnv(), NEW_SHAPE)


def test_aec_api():
    api_test(ReshapeObservation(DummyAEC(), NEW_SHAPE), num_cycles=5)


def test_parallel_api():
    parallel_api_test(
        ReshapeObservationParallel(DummyParallel(), NEW_SHAPE), num_cycles=5
    )


def test_rejects_parallel_env():
    with pytest.raises(AssertionError):
        ReshapeObservation(DummyParallel(), NEW_SHAPE)
