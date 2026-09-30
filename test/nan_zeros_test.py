from __future__ import annotations

import numpy as np
import pytest
from gymnasium.spaces import Box, Discrete

from pettingzoo.test import api_test, parallel_api_test
from pettingzoo.utils.wrappers import NanZerosParallelV1, NanZerosV1

from .scale_action_test import DummyAEC, DummyParallel


def test_aec_replaces_nan_with_zeros():
    env = NanZerosV1(DummyAEC())
    env.reset()
    agent = env.agent_selection
    with pytest.warns(UserWarning, match="NaN"):
        env.step(np.array([np.nan, 0.5, 0.5], dtype=np.float32))
    received = env.unwrapped.received[agent]
    assert received.dtype == np.float32
    np.testing.assert_array_equal(received, np.zeros(3, dtype=np.float32))


def test_aec_passes_clean_action_through():
    env = NanZerosV1(DummyAEC())
    env.reset()
    agent = env.agent_selection
    action = np.array([0.1, 0.2, 0.3], dtype=np.float32)
    env.step(action)
    np.testing.assert_array_equal(env.unwrapped.received[agent], action)


def test_parallel_only_nan_agent_is_replaced():
    env = NanZerosParallelV1(DummyParallel())
    env.reset()
    clean = np.array([0.1, 0.2, 0.3], dtype=np.float32)
    with pytest.warns(UserWarning, match="NaN"):
        env.step({"agent_0": np.full(3, np.nan, dtype=np.float32), "agent_1": clean})
    received = env.unwrapped.received
    np.testing.assert_array_equal(received["agent_0"], np.zeros(3))
    np.testing.assert_array_equal(received["agent_1"], clean)


def test_scalar_box_action():
    env = NanZerosV1(DummyAEC(lambda agent: Box(-1.0, 1.0, shape=(), dtype=np.float64)))
    env.reset()
    agent = env.agent_selection
    with pytest.warns(UserWarning):
        env.step(np.float64("nan"))
    assert env.unwrapped.received[agent].shape == ()
    assert env.unwrapped.received[agent] == 0


def test_space_excluding_zero_is_rejected():
    with pytest.raises(ValueError, match="zero is outside"):
        NanZerosV1(DummyAEC(lambda agent: Box(1.0, 2.0, shape=(3,), dtype=np.float32)))


def test_non_float_space_is_rejected():
    with pytest.raises(TypeError):
        NanZerosV1(DummyAEC(lambda agent: Discrete(3)))


def test_aec_api():
    api_test(NanZerosV1(DummyAEC(lambda a: Box(-1.0, 1.0, (3,), np.float32))), 5)


def test_parallel_api():
    parallel_api_test(
        NanZerosParallelV1(DummyParallel(lambda a: Box(-1.0, 1.0, (3,), np.float32))), 5
    )
