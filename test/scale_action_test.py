from __future__ import annotations

import functools

import numpy as np
import pytest
from gymnasium.spaces import Box, Discrete

from pettingzoo.test import api_test, parallel_api_test
from pettingzoo.utils.env import AECEnv, ParallelEnv
from pettingzoo.utils.wrappers import ScaleActionParallelV1, ScaleActionV1

AGENTS = ["agent_0", "agent_1"]

OBS = np.array([0.5, -0.5], dtype=np.float32)
OBS_SPACE = Box(low=-1.0, high=1.0, shape=(2,), dtype=np.float32)


@functools.cache
def act_space(agent):
    if agent == "agent_0":
        return Box(low=-1.0, high=1.0, shape=(3,), dtype=np.float32)
    return Box(low=0.0, high=10.0, shape=(3,), dtype=np.float32)


class DummyAEC(AECEnv):
    metadata = {"render_modes": [], "name": "dummy_aec"}

    def __init__(self, action_space_fn=act_space):
        super().__init__()
        self.possible_agents = list(AGENTS)
        self._action_space_fn = action_space_fn
        self.received = {}

    def observation_space(self, agent):
        return OBS_SPACE

    @functools.cache
    def action_space(self, agent):
        return self._action_space_fn(agent)

    def reset(self, seed=None, options=None):
        self.agents = list(self.possible_agents)
        self.rewards = dict.fromkeys(self.agents, 0.0)
        self._cumulative_rewards = dict.fromkeys(self.agents, 0.0)
        self.terminations = dict.fromkeys(self.agents, False)
        self.truncations = dict.fromkeys(self.agents, False)
        self.infos = {a: {} for a in self.agents}
        self.received = {}
        self._idx = 0
        self._step_count = 0
        self.agent_selection = self.agents[0]

    def observe(self, agent):
        return OBS

    def step(self, action):
        self.received[self.agent_selection] = action
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

    def __init__(self, action_space_fn=act_space):
        super().__init__()
        self.possible_agents = list(AGENTS)
        self._action_space_fn = action_space_fn
        self.received = {}

    def observation_space(self, agent):
        return OBS_SPACE

    @functools.cache
    def action_space(self, agent):
        return self._action_space_fn(agent)

    def reset(self, seed=None, options=None):
        self.agents = list(self.possible_agents)
        self.received = {}
        self._step_count = 0
        return dict.fromkeys(self.agents, OBS), {a: {} for a in self.agents}

    def step(self, actions):
        self.received = dict(actions)
        self._step_count += 1
        done = self._step_count >= 8
        obs = dict.fromkeys(self.agents, OBS)
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


def discrete_space(agent):
    return Discrete(5)


@pytest.mark.parametrize("agent", AGENTS)
def test_aec_action_space_bounds(agent):
    space = ScaleActionV1(DummyAEC(), 2.0).action_space(agent)
    inner = act_space(agent)
    assert isinstance(space, Box)
    assert space.shape == inner.shape
    assert space.dtype == inner.dtype
    assert np.allclose(space.low, inner.low * 2.0)
    assert np.allclose(space.high, inner.high * 2.0)


@pytest.mark.parametrize("agent", AGENTS)
def test_parallel_action_space_bounds(agent):
    space = ScaleActionParallelV1(DummyParallel(), 0.5).action_space(agent)
    inner = act_space(agent)
    assert np.allclose(space.low, inner.low * 0.5)
    assert np.allclose(space.high, inner.high * 0.5)


def test_symmetric_box_stays_symmetric():
    space = ScaleActionV1(DummyAEC(), 3.0).action_space("agent_0")
    assert np.allclose(space.low, -3.0)
    assert np.allclose(space.high, 3.0)


@pytest.mark.parametrize("agent", AGENTS)
def test_scale_one_is_a_noop(agent):
    inner = DummyAEC()
    env = ScaleActionV1(inner, 1.0)
    assert env.action_space(agent) == act_space(agent)

    env.reset(seed=0)
    action = np.array([0.25, 0.5, 1.0], dtype=np.float32)
    while env.agent_selection != agent:
        env.step(np.zeros(3, dtype=np.float32))
    env.step(action)
    assert np.allclose(inner.received[agent], action)


def test_out_of_range_action_is_passed_through():
    """The wrapper rescales, it does not sanitise. Out of range stays out of range."""
    inner = DummyAEC()
    env = ScaleActionV1(inner, 2.0)
    env.reset(seed=0)
    env.step(np.array([100.0, -100.0, 0.0], dtype=np.float32))
    assert np.allclose(inner.received["agent_0"], [50.0, -50.0, 0.0])


def test_endpoint_of_advertised_space_lands_on_inner_bound():
    """The float round trip overshoots at the bounds, so the bounds are clipped."""
    inner_space = Box(low=-1.7, high=1.7, shape=(1,), dtype=np.float32)
    inner = DummyAEC(lambda agent: inner_space)
    env = ScaleActionV1(inner, 3.0)
    env.reset(seed=0)

    high = env.action_space("agent_0").high.copy()
    assert float(high[0]) / 3.0 > float(inner_space.high[0])  # the overshoot
    env.step(high)
    assert inner.received["agent_0"] == inner_space.high


def test_aec_step_divides_by_scale():
    inner = DummyAEC()
    env = ScaleActionV1(inner, 2.0)
    env.reset(seed=0)

    env.step(np.array([2.0, -1.0, 0.5], dtype=np.float32))
    received = inner.received["agent_0"]
    assert np.allclose(received, [1.0, -0.5, 0.25])
    assert received.dtype == act_space("agent_0").dtype


def test_parallel_step_divides_by_scale():
    inner = DummyParallel()
    env = ScaleActionParallelV1(inner, 2.0)
    env.reset(seed=0)

    env.step(
        {
            "agent_0": np.array([2.0, -1.0, 0.5], dtype=np.float32),
            "agent_1": np.array([20.0, 10.0, 0.0], dtype=np.float32),
        }
    )
    assert np.allclose(inner.received["agent_0"], [1.0, -0.5, 0.25])
    assert np.allclose(inner.received["agent_1"], [10.0, 5.0, 0.0])


@pytest.mark.parametrize("scale", [0.1, 0.5, 1.0, 2.0, 3.0, 10.0, -0.3, -2.0])
@pytest.mark.parametrize("bound", [1.0, 1.7, 3.3])
def test_action_from_advertised_space_is_valid_inside(scale, bound):
    """Anything the advertised space accepts has to be valid for the wrapped env."""
    inner_space = Box(low=-bound, high=bound, shape=(2,), dtype=np.float32)
    inner = DummyAEC(lambda agent: inner_space)
    env = ScaleActionV1(inner, scale)
    env.reset(seed=0)

    space = env.action_space("agent_0")
    space.seed(0)
    actions = [space.low.copy(), space.high.copy()]
    actions += [space.sample() for _ in range(50)]

    for action in actions:
        assert space.contains(action)
        agent = env.agent_selection
        env.step(action)
        received = inner.received[agent]
        assert inner_space.contains(received)
        expected = np.clip(
            np.asarray(action, dtype=np.float64) / scale,
            inner_space.low,
            inner_space.high,
        )
        assert np.allclose(received, expected, rtol=1e-6, atol=1e-6)


@pytest.mark.parametrize("scale", [0.1, 3.0, -0.3])
def test_parallel_action_from_advertised_space_is_valid_inside(scale):
    inner_space = Box(low=-1.7, high=1.7, shape=(2,), dtype=np.float32)
    inner = DummyParallel(lambda agent: inner_space)
    env = ScaleActionParallelV1(inner, scale)
    env.reset(seed=0)

    space = env.action_space("agent_0")
    space.seed(0)
    for action in [space.low.copy(), space.high.copy()] + [space.sample()]:
        env.step(dict.fromkeys(AGENTS, action))
        expected = np.clip(
            np.asarray(action, dtype=np.float64) / scale,
            inner_space.low,
            inner_space.high,
        )
        for agent in AGENTS:
            assert inner_space.contains(inner.received[agent])
            assert np.allclose(inner.received[agent], expected, rtol=1e-6, atol=1e-6)


def test_negative_scale_swaps_bounds():
    env = ScaleActionV1(DummyAEC(), -2.0)
    space = env.action_space("agent_1")
    inner = act_space("agent_1")
    assert np.allclose(space.low, inner.high * -2.0)
    assert np.allclose(space.high, inner.low * -2.0)


def test_negative_scale_maps_back_into_inner_space():
    inner = DummyAEC()
    env = ScaleActionV1(inner, -2.0)
    env.reset(seed=0)
    env.step(np.zeros(3, dtype=np.float32))  # agent_0's turn

    env.step(np.array([-20.0, -10.0, 0.0], dtype=np.float32))
    received = inner.received["agent_1"]
    assert np.allclose(received, [10.0, 5.0, 0.0])
    assert act_space("agent_1").contains(received)


def test_zero_scale_is_rejected():
    with pytest.raises(AssertionError):
        ScaleActionV1(DummyAEC(), 0)
    with pytest.raises(AssertionError):
        ScaleActionParallelV1(DummyParallel(), 0)


def test_non_box_action_space_is_rejected():
    with pytest.raises(AssertionError):
        ScaleActionV1(DummyAEC(discrete_space), 2.0)
    with pytest.raises(AssertionError):
        ScaleActionParallelV1(DummyParallel(discrete_space), 2.0)


def test_none_action_passes_through():
    inner = DummyAEC()
    env = ScaleActionV1(inner, 2.0)
    env.reset(seed=0)
    env.step(None)
    assert inner.received["agent_0"] is None


def test_aec_api():
    api_test(ScaleActionV1(DummyAEC(), 2.0), num_cycles=5)


def test_parallel_api():
    parallel_api_test(ScaleActionParallelV1(DummyParallel(), 2.0), num_cycles=5)


def test_rejects_parallel_env():
    with pytest.raises(AssertionError):
        ScaleActionV1(DummyParallel(), 2.0)
