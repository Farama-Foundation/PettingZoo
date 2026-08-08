from __future__ import annotations

import functools

import numpy as np
import pytest
from gymnasium.spaces import Box, Dict, Discrete
from gymnasium.spaces.utils import flatten

from pettingzoo.test import api_test, parallel_api_test
from pettingzoo.utils.env import AECEnv, ParallelEnv
from pettingzoo.utils.wrappers import FlattenObservation, FlattenObservationParallel

AGENTS = ["agent_0", "agent_1"]

FIXED_OBS = {
    "agent_0": np.arange(6, dtype=np.float32).reshape(2, 3) / 10.0,
    "agent_1": {"a": np.array([-1.0, -0.5, 0.0, 0.5], dtype=np.float32), "b": 2},
}


@functools.cache
def obs_space(agent):
    if agent == "agent_0":
        return Box(low=0.0, high=1.0, shape=(2, 3), dtype=np.float32)
    return Dict(
        {"a": Box(low=-1.0, high=1.0, shape=(4,), dtype=np.float32), "b": Discrete(3)}
    )


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


@pytest.mark.parametrize("agent", AGENTS)
def test_aec_observation_space_is_flat(agent):
    space = FlattenObservation(DummyAEC()).observation_space(agent)
    assert isinstance(space, Box)
    assert len(space.shape) == 1


@pytest.mark.parametrize("agent", AGENTS)
def test_parallel_observation_space_is_flat(agent):
    space = FlattenObservationParallel(DummyParallel()).observation_space(agent)
    assert isinstance(space, Box)
    assert len(space.shape) == 1


def test_flattened_sizes():
    env = FlattenObservation(DummyAEC())
    assert env.observation_space("agent_0").shape == (6,)
    assert env.observation_space("agent_1").shape == (7,)


@pytest.mark.parametrize("agent", AGENTS)
def test_aec_observe_matches_flatten(agent):
    inner = DummyAEC()
    env = FlattenObservation(inner)
    env.reset(seed=0)

    obs = env.observe(agent)
    assert np.allclose(obs, flatten(obs_space(agent), FIXED_OBS[agent]))
    assert env.observation_space(agent).contains(obs)

    raw = inner.observe(agent)
    assert not (isinstance(raw, np.ndarray) and raw.shape == np.asarray(obs).shape)


@pytest.mark.parametrize("agent", AGENTS)
def test_parallel_reset_matches_flatten(agent):
    env = FlattenObservationParallel(DummyParallel())
    obs, _ = env.reset(seed=0)
    assert np.allclose(obs[agent], flatten(obs_space(agent), FIXED_OBS[agent]))
    assert env.observation_space(agent).contains(obs[agent])


@pytest.mark.parametrize("agent", AGENTS)
def test_parallel_step_matches_flatten(agent):
    env = FlattenObservationParallel(DummyParallel())
    env.reset(seed=0)
    obs, _, _, _, _ = env.step(dict.fromkeys(env.agents, 0))
    assert np.allclose(obs[agent], flatten(obs_space(agent), FIXED_OBS[agent]))


@pytest.mark.parametrize("agent", AGENTS)
def test_aec_last_matches_flatten(agent):
    env = FlattenObservation(DummyAEC())
    env.reset(seed=0)
    while env.agent_selection != agent:
        env.step(0)

    obs, _, _, _, _ = env.last()
    assert np.allclose(obs, flatten(obs_space(agent), FIXED_OBS[agent]))


def test_observe_passes_through_none():
    class NoneObsEnv(DummyAEC):
        def observe(self, agent):
            return None

    env = FlattenObservation(NoneObsEnv())
    env.reset(seed=0)
    assert env.observe("agent_0") is None


def test_aec_api():
    api_test(FlattenObservation(DummyAEC()), num_cycles=5)


def test_parallel_api():
    parallel_api_test(FlattenObservationParallel(DummyParallel()), num_cycles=5)


def test_rejects_parallel_env():
    with pytest.raises(AssertionError):
        FlattenObservation(DummyParallel())
