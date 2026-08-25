from __future__ import annotations

import functools

import numpy as np
import pytest
from gymnasium.spaces import Box, Discrete

from pettingzoo.test import api_test, parallel_api_test
from pettingzoo.utils.env import AECEnv, ParallelEnv
from pettingzoo.utils.wrappers import (
    ColorReductionObservation,
    ColorReductionObservationParallel,
)

AGENTS = ["agent_0", "agent_1"]

DEFAULT_SPACE = Box(low=0, high=255, shape=(2, 2, 3), dtype=np.uint8)

# 2x2 RGB images, one per agent.
FIXED_OBS = {
    "agent_0": np.array(
        [[[10, 20, 30], [0, 0, 0]], [[255, 255, 255], [100, 150, 200]]], dtype=np.uint8
    ),
    "agent_1": np.array(
        [[[1, 2, 3], [4, 5, 6]], [[7, 8, 9], [10, 11, 12]]], dtype=np.uint8
    ),
}

# 0.299 * 10 + 0.587 * 20 + 0.114 * 30 = 18.15, and so on, truncated to uint8.
EXPECTED_GRAY_0 = np.array([[18, 0], [255, 140]], dtype=np.uint8)

# A space whose upper bound differs per channel, so the four modes give four
# different reduced spaces: 18 for full (18.15 truncated), then 10, 20, 30.
CHANNEL_SPACE = Box(
    low=0,
    high=np.tile(np.array([10, 20, 30], dtype=np.uint8), (2, 2, 1)),
    dtype=np.uint8,
)
CHANNEL_HIGHS = [("full", 18), ("R", 10), ("G", 20), ("B", 30)]

# A non-uint8 space, to pin down what each mode does to the dtype.
FLOAT_SPACE = Box(low=0.0, high=1.0, shape=(2, 2, 3), dtype=np.float32)
FLOAT_OBS = (np.arange(12, dtype=np.float32) / 11.0).reshape(2, 2, 3)


class DummyAEC(AECEnv):
    metadata = {"render_modes": [], "name": "dummy_aec"}

    def __init__(self, space=None, obs=None):
        super().__init__()
        self.possible_agents = list(AGENTS)
        self._space = DEFAULT_SPACE if space is None else space
        self._obs = FIXED_OBS if obs is None else obs

    def observation_space(self, agent):
        return self._space

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
        return self._obs[agent]

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

    def __init__(self, space=None, obs=None):
        super().__init__()
        self.possible_agents = list(AGENTS)
        self._space = DEFAULT_SPACE if space is None else space
        self._obs = FIXED_OBS if obs is None else obs

    def observation_space(self, agent):
        return self._space

    @functools.cache
    def action_space(self, agent):
        return Discrete(2)

    def reset(self, seed=None, options=None):
        self.agents = list(self.possible_agents)
        self._step_count = 0
        return dict(self._obs), {a: {} for a in self.agents}

    def step(self, actions):
        self._step_count += 1
        done = self._step_count >= 8
        obs = dict(self._obs)
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


def float_obs():
    return dict.fromkeys(AGENTS, FLOAT_OBS)


@pytest.mark.parametrize("mode", ["full", "R", "G", "B"])
@pytest.mark.parametrize("agent", AGENTS)
def test_aec_observation_space_drops_channel_axis(mode, agent):
    space = ColorReductionObservation(DummyAEC(), mode).observation_space(agent)
    assert isinstance(space, Box)
    assert space.shape == (2, 2)
    assert space.dtype == np.uint8
    assert np.array_equal(space.low, np.zeros((2, 2), dtype=np.uint8))
    assert np.array_equal(space.high, np.full((2, 2), 255, dtype=np.uint8))


@pytest.mark.parametrize("mode", ["full", "R", "G", "B"])
def test_parallel_observation_space_drops_channel_axis(mode):
    space = ColorReductionObservationParallel(DummyParallel(), mode).observation_space(
        "agent_0"
    )
    assert space.shape == (2, 2)
    assert space.dtype == np.uint8


@pytest.mark.parametrize("mode,high", CHANNEL_HIGHS)
def test_aec_space_bounds_follow_the_mode(mode, high):
    space = ColorReductionObservation(
        DummyAEC(space=CHANNEL_SPACE), mode
    ).observation_space("agent_0")
    assert np.array_equal(space.low, np.zeros((2, 2), dtype=np.uint8))
    assert np.array_equal(space.high, np.full((2, 2), high, dtype=np.uint8))


@pytest.mark.parametrize("mode,high", CHANNEL_HIGHS)
def test_parallel_space_bounds_follow_the_mode(mode, high):
    space = ColorReductionObservationParallel(
        DummyParallel(space=CHANNEL_SPACE), mode
    ).observation_space("agent_0")
    assert np.array_equal(space.high, np.full((2, 2), high, dtype=np.uint8))


def test_aec_grayscale_matches_hand_computed_values():
    env = ColorReductionObservation(DummyAEC(), "full")
    env.reset(seed=0)

    obs = env.observe("agent_0")
    assert np.array_equal(obs, EXPECTED_GRAY_0)
    assert obs.dtype == np.uint8
    assert env.observation_space("agent_0").contains(obs)


@pytest.mark.parametrize("mode,channel", [("R", 0), ("G", 1), ("B", 2)])
@pytest.mark.parametrize("agent", AGENTS)
def test_aec_single_channel_modes(mode, channel, agent):
    env = ColorReductionObservation(DummyAEC(), mode)
    env.reset(seed=0)

    obs = env.observe(agent)
    assert np.array_equal(obs, FIXED_OBS[agent][:, :, channel])
    assert env.observation_space(agent).contains(obs)


@pytest.mark.parametrize("mode,channel", [("R", 0), ("G", 1), ("B", 2)])
def test_aec_single_channel_modes_keep_the_input_dtype(mode, channel):
    env = ColorReductionObservation(DummyAEC(space=FLOAT_SPACE, obs=float_obs()), mode)
    env.reset(seed=0)

    space = env.observation_space("agent_0")
    assert space.dtype == np.float32
    assert np.array_equal(space.high, np.ones((2, 2), dtype=np.float32))

    obs = env.observe("agent_0")
    assert obs.dtype == np.float32
    assert np.array_equal(obs, FLOAT_OBS[:, :, channel])
    assert space.contains(obs)


@pytest.mark.parametrize("mode,channel", [("R", 0), ("G", 1), ("B", 2)])
def test_parallel_single_channel_modes_keep_the_input_dtype(mode, channel):
    env = ColorReductionObservationParallel(
        DummyParallel(space=FLOAT_SPACE, obs=float_obs()), mode
    )
    obs, _ = env.reset(seed=0)

    assert env.observation_space("agent_0").dtype == np.float32
    assert obs["agent_0"].dtype == np.float32
    assert np.array_equal(obs["agent_0"], FLOAT_OBS[:, :, channel])


def test_full_mode_returns_uint8_for_a_float_space():
    # SuperSuit casts the grayscale result to uint8 whatever went in, so a float
    # space in [0, 1] comes out as a uint8 Box and the values truncate to 0.
    env = ColorReductionObservation(
        DummyAEC(space=FLOAT_SPACE, obs=float_obs()), "full"
    )
    env.reset(seed=0)

    space = env.observation_space("agent_0")
    assert space.dtype == np.uint8
    assert np.array_equal(space.high, np.ones((2, 2), dtype=np.uint8))

    obs = env.observe("agent_0")
    assert obs.dtype == np.uint8
    assert np.array_equal(obs, np.zeros((2, 2), dtype=np.uint8))


def test_observation_does_not_alias_the_env_buffer():
    inner = DummyAEC()
    env = ColorReductionObservation(inner, "R")
    env.reset(seed=0)

    obs = env.observe("agent_0")
    obs[0, 0] = 99
    assert np.array_equal(inner.observe("agent_0"), FIXED_OBS["agent_0"])


def test_aec_last_is_reduced():
    env = ColorReductionObservation(DummyAEC(), "full")
    env.reset(seed=0)
    while env.agent_selection != "agent_0":
        env.step(0)

    obs, _, _, _, _ = env.last()
    assert np.array_equal(obs, EXPECTED_GRAY_0)


def test_parallel_reset_and_step_are_reduced():
    env = ColorReductionObservationParallel(DummyParallel(), "full")

    obs, _ = env.reset(seed=0)
    assert np.array_equal(obs["agent_0"], EXPECTED_GRAY_0)
    assert env.observation_space("agent_0").contains(obs["agent_0"])

    obs, _, _, _, _ = env.step(dict.fromkeys(env.agents, 0))
    assert np.array_equal(obs["agent_0"], EXPECTED_GRAY_0)
    assert obs["agent_1"].shape == (2, 2)


def test_parallel_single_channel_mode():
    env = ColorReductionObservationParallel(DummyParallel(), "G")
    obs, _ = env.reset(seed=0)
    assert np.array_equal(obs["agent_1"], FIXED_OBS["agent_1"][:, :, 1])


def test_default_mode_is_full():
    env = ColorReductionObservation(DummyAEC())
    env.reset(seed=0)
    assert np.array_equal(env.observe("agent_0"), EXPECTED_GRAY_0)


def test_observe_passes_through_none():
    class NoneObsEnv(DummyAEC):
        def observe(self, agent):
            return None

    env = ColorReductionObservation(NoneObsEnv())
    env.reset(seed=0)
    assert env.observe("agent_0") is None


def test_aec_str():
    inner = DummyAEC()
    assert (
        str(ColorReductionObservation(inner)) == f"ColorReductionObservation<{inner}>"
    )


def test_parallel_str():
    inner = DummyParallel()
    assert (
        str(ColorReductionObservationParallel(inner))
        == f"ColorReductionObservationParallel<{inner}>"
    )


def test_aec_api():
    api_test(ColorReductionObservation(DummyAEC()), num_cycles=5)


def test_parallel_api():
    parallel_api_test(ColorReductionObservationParallel(DummyParallel()), num_cycles=5)


def test_rejects_parallel_env():
    with pytest.raises(AssertionError):
        ColorReductionObservation(DummyParallel())


@pytest.mark.parametrize("mode", ["gray", "r", "", "RGB", 0])
def test_rejects_unknown_mode(mode):
    with pytest.raises(AssertionError):
        ColorReductionObservation(DummyAEC(), mode)
    with pytest.raises(AssertionError):
        ColorReductionObservationParallel(DummyParallel(), mode)


@pytest.mark.parametrize(
    "space",
    [
        Discrete(4),
        Box(low=0, high=1, shape=(6,), dtype=np.float32),
        Box(low=0, high=255, shape=(2, 2, 4), dtype=np.uint8),
        Box(low=0, high=255, shape=(2, 2, 3, 1), dtype=np.uint8),
    ],
)
def test_rejects_non_image_observation_space(space):
    with pytest.raises(AssertionError, match="agent_0"):
        ColorReductionObservation(DummyAEC(space=space))
    with pytest.raises(AssertionError, match="agent_0"):
        ColorReductionObservationParallel(DummyParallel(space=space))
