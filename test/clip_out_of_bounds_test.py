from __future__ import annotations

import logging

import numpy as np
import pytest

from pettingzoo.test import parallel_api_test
from pettingzoo.utils.wrappers import ClipOutOfBoundsParallelV1

from .scale_action_test import DummyAEC, DummyParallel, discrete_space


def test_parallel_clips_each_agents_box_without_mutating_input(caplog):
    inner = DummyParallel()
    env = ClipOutOfBoundsParallelV1(inner)
    env.reset()
    first = np.array([-2.0, 0.0, 0.5], dtype=np.float32)
    second = np.array([20.0, -3.0, 3.0], dtype=np.float32)
    actions = {"agent_0": first, "agent_1": second}

    with caplog.at_level(logging.WARNING, logger="pettingzoo.utils.env_logger"):
        env.step(actions)

    np.testing.assert_array_equal(inner.received["agent_0"], [-1.0, 0.0, 0.5])
    np.testing.assert_array_equal(inner.received["agent_1"], [10.0, 0.0, 3.0])
    np.testing.assert_array_equal(first, [-2.0, 0.0, 0.5])
    np.testing.assert_array_equal(second, [20.0, -3.0, 3.0])
    assert len(caplog.records) == 2
    assert all("clipping to space" in record.message for record in caplog.records)
    assert env.action_space("agent_0") is inner.action_space("agent_0")
    assert env.action_space("agent_1") is inner.action_space("agent_1")


def test_parallel_keeps_in_range_actions_unchanged(caplog):
    inner = DummyParallel()
    env = ClipOutOfBoundsParallelV1(inner)
    env.reset()
    valid = np.array([0.2, 0.3, 0.4], dtype=np.float32)

    with caplog.at_level(logging.WARNING, logger="pettingzoo.utils.env_logger"):
        env.step({"agent_0": valid})

    assert inner.received == {"agent_0": valid}
    assert inner.received["agent_0"] is valid
    assert not caplog.records


def test_parallel_rejects_wrong_action_shape():
    inner = DummyParallel()
    env = ClipOutOfBoundsParallelV1(inner)
    env.reset()

    with pytest.raises(AssertionError, match=r"action should have shape \(3,\)"):
        env.step({"agent_0": np.array([2.0], dtype=np.float32)})
    assert inner.received == {}


def test_parallel_rejects_nan_action():
    inner = DummyParallel()
    env = ClipOutOfBoundsParallelV1(inner)
    env.reset()

    with pytest.raises(AssertionError, match="nan action"):
        env.step({"agent_0": np.array([np.nan, 0.0, 0.0], dtype=np.float32)})
    assert inner.received == {}


def test_parallel_rejects_non_box_space_and_aec_environment():
    with pytest.raises(AssertionError, match="Box spaces"):
        ClipOutOfBoundsParallelV1(DummyParallel(discrete_space))
    with pytest.raises(AssertionError, match="parallel environments"):
        ClipOutOfBoundsParallelV1(DummyAEC())


def test_parallel_api():
    parallel_api_test(ClipOutOfBoundsParallelV1(DummyParallel()), num_cycles=5)
