from __future__ import annotations

import logging
import pickle

import numpy as np
import pytest

from pettingzoo.test import api_test, parallel_api_test
from pettingzoo.utils.env import AECEnv, ParallelEnv
from pettingzoo.utils.wrappers import ClipOutOfBoundsWrapper

from .scale_action_test import DummyAEC, DummyParallel, discrete_space


def test_parallel_clips_each_agents_box_without_mutating_input(caplog):
    inner = DummyParallel()
    env = ClipOutOfBoundsWrapper(inner)
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
    env = ClipOutOfBoundsWrapper(inner)
    env.reset()
    valid = np.array([0.2, 0.3, 0.4], dtype=np.float32)

    with caplog.at_level(logging.WARNING, logger="pettingzoo.utils.env_logger"):
        env.step({"agent_0": valid})

    assert inner.received == {"agent_0": valid}
    assert inner.received["agent_0"] is valid
    assert not caplog.records


def test_parallel_rejects_wrong_action_shape():
    inner = DummyParallel()
    env = ClipOutOfBoundsWrapper(inner)
    env.reset()

    with pytest.raises(AssertionError, match=r"action should have shape \(3,\)"):
        env.step({"agent_0": np.array([2.0], dtype=np.float32)})
    assert inner.received == {}


def test_parallel_rejects_nan_action():
    inner = DummyParallel()
    env = ClipOutOfBoundsWrapper(inner)
    env.reset()

    with pytest.raises(AssertionError, match="nan action"):
        env.step({"agent_0": np.array([np.nan, 0.0, 0.0], dtype=np.float32)})
    assert inner.received == {}


@pytest.mark.parametrize("env_type", [DummyAEC, DummyParallel])
def test_rejects_non_box_space(env_type):
    with pytest.raises(AssertionError, match="Box spaces"):
        ClipOutOfBoundsWrapper(env_type(discrete_space))


def test_parallel_api():
    env = ClipOutOfBoundsWrapper(DummyParallel())
    assert isinstance(env, ParallelEnv)
    assert not isinstance(env, AECEnv)
    parallel_api_test(env, num_cycles=5)


def test_aec_api():
    env = ClipOutOfBoundsWrapper(DummyAEC())
    assert isinstance(env, AECEnv)
    assert not isinstance(env, ParallelEnv)
    api_test(env, num_cycles=10)


def test_aec_clips_actions_and_keeps_in_range_actions_unchanged(caplog):
    inner = DummyAEC()
    env = ClipOutOfBoundsWrapper(inner)
    env.reset()
    action = np.array([-2.0, 0.0, 0.5], dtype=np.float32)
    valid = np.array([2.0, 3.0, 4.0], dtype=np.float32)

    with caplog.at_level(logging.WARNING, logger="pettingzoo.utils.env_logger"):
        assert env.step(action) is None
        env.step(valid)

    np.testing.assert_array_equal(inner.received["agent_0"], [-1.0, 0.0, 0.5])
    np.testing.assert_array_equal(action, [-2.0, 0.0, 0.5])
    assert inner.received["agent_1"] is valid
    assert len(caplog.records) == 1


@pytest.mark.parametrize(
    ("action", "error"),
    [
        (np.array([2.0], dtype=np.float32), "action should have shape"),
        (np.array([np.nan, 0.0, 0.0], dtype=np.float32), "nan action"),
    ],
)
def test_aec_rejects_malformed_actions(action, error):
    inner = DummyAEC()
    env = ClipOutOfBoundsWrapper(inner)
    env.reset()

    with pytest.raises(AssertionError, match=error):
        env.step(action)
    assert inner.received == {}


def test_aec_dead_agent_step():
    env = ClipOutOfBoundsWrapper(DummyAEC())
    env.reset()
    env.terminations[env.agent_selection] = True
    env.step(None)
    assert "agent_0" not in env.agents


@pytest.mark.parametrize("env_type", [DummyAEC, DummyParallel])
def test_wrapped_environment_pickle_round_trip(env_type):
    env = ClipOutOfBoundsWrapper(env_type())
    env.reset()
    restored = pickle.loads(pickle.dumps(env))
    action = np.array([-2.0, 0.0, 0.5], dtype=np.float32)

    if isinstance(restored, AECEnv):
        assert restored.step(action) is None
    else:
        assert isinstance(restored, ParallelEnv)
        assert len(restored.step({"agent_0": action})) == 5
    np.testing.assert_array_equal(restored.env.received["agent_0"], [-1.0, 0.0, 0.5])
