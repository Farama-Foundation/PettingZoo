from __future__ import annotations

import numpy as np
import pytest
from gymnasium.spaces import Box, Discrete, MultiDiscrete

from pettingzoo.test import api_test, parallel_api_test
from pettingzoo.utils.wrappers import PadActionSpaceParallelV1, PadActionSpaceV1

from .scale_action_test import DummyAEC, DummyParallel

DISCRETE = {"agent_0": Discrete(5), "agent_1": Discrete(2)}
BOXES = {
    "agent_0": Box(low=-1.0, high=1.0, shape=(3,), dtype=np.float32),
    "agent_1": Box(low=0.0, high=2.0, shape=(1,), dtype=np.float32),
}


def discrete(agent):
    return DISCRETE[agent]


def boxes(agent):
    return BOXES[agent]


def test_discrete_shared_space():
    env = PadActionSpaceV1(DummyAEC(discrete))
    assert env.action_space("agent_0") == Discrete(5)
    assert env.action_space("agent_1") == Discrete(5)


def test_box_shared_space():
    env = PadActionSpaceParallelV1(DummyParallel(boxes))
    for agent in BOXES:
        space = env.action_space(agent)
        assert space.shape == (3,)
        np.testing.assert_array_equal(space.low, [-1.0, -1.0, -1.0])
        # agent_1's missing dims are padded with its own max bound, as in SuperSuit
        np.testing.assert_array_equal(space.high, [2.0, 2.0, 2.0])


@pytest.mark.parametrize(("action", "expected"), [(1, 1), (4, 0)])
def test_aec_discrete_padded_region_maps_to_zero(action, expected):
    env = PadActionSpaceV1(DummyAEC(discrete))
    env.reset()
    env.step(0)  # agent_0
    env.step(action)  # agent_1 only has actions 0 and 1
    assert env.unwrapped.received["agent_1"] == expected


def test_aec_box_action_is_sliced():
    env = PadActionSpaceV1(DummyAEC(boxes))
    env.reset()
    first = np.array([0.1, 0.2, 0.3], dtype=np.float32)
    env.step(first)
    env.step(np.array([1.5, 0.9, 0.9], dtype=np.float32))
    received = env.unwrapped.received
    np.testing.assert_array_equal(received["agent_0"], first)
    assert received["agent_1"].shape == (1,)
    assert received["agent_1"][0] == np.float32(1.5)


def test_parallel_each_agent_is_unpadded():
    env = PadActionSpaceParallelV1(DummyParallel(discrete))
    env.reset()
    env.step({"agent_0": 4, "agent_1": 3})
    assert env.unwrapped.received == {"agent_0": 4, "agent_1": 0}


@pytest.mark.parametrize(
    "wrapper,dummy",
    [(PadActionSpaceV1, DummyAEC), (PadActionSpaceParallelV1, DummyParallel)],
)
@pytest.mark.parametrize("dtype", [np.float32, np.int16])
@pytest.mark.parametrize(
    "empty_shape,other_shape",
    [((0,), (3,)), ((0, 2), (2, 3)), ((2, 0), (3, 2)), ((0,), (0,))],
)
def test_empty_box_actions(wrapper, dummy, dtype, empty_shape, other_shape):
    spaces = {
        "agent_0": Box(2, 5, shape=empty_shape, dtype=dtype),
        "agent_1": Box(2, 5, shape=other_shape, dtype=dtype),
    }
    inner = dummy(spaces.__getitem__)
    env = wrapper(inner)
    try:
        env.reset(seed=0)
        action = np.full(other_shape, 3, dtype=dtype)
        for agent in spaces:
            assert env.action_space(agent).shape == other_shape
            assert env.action_space(agent).dtype == dtype
            assert env.action_space(agent).contains(action)

        if isinstance(env, PadActionSpaceV1):
            env.step(action)
            env.step(action)
        else:
            env.step(dict.fromkeys(spaces, action))

        for agent, space in spaces.items():
            expected = np.full(space.shape, 3, dtype=dtype)
            np.testing.assert_array_equal(inner.received[agent], expected)
            assert inner.received[agent].dtype == dtype
            assert space.contains(inner.received[agent])
    finally:
        env.close()


def test_discrete_with_start_maps_to_its_first_action():
    spaces = {"agent_0": Discrete(4), "agent_1": Discrete(2, start=1)}
    env = PadActionSpaceParallelV1(DummyParallel(spaces.__getitem__))
    env.reset()
    env.step({"agent_0": 0, "agent_1": 3})
    assert env.unwrapped.received["agent_1"] == 1


@pytest.mark.parametrize(
    "spaces",
    [
        {"agent_0": Discrete(2), "agent_1": Box(0.0, 1.0, (2,), np.float32)},
        {"agent_0": MultiDiscrete([2, 2]), "agent_1": MultiDiscrete([2, 2])},
        {
            "agent_0": Box(0.0, 1.0, (2,), np.float32),
            "agent_1": Box(0.0, 1.0, (2, 2), np.float32),
        },
    ],
)
def test_incompatible_spaces_are_rejected(spaces):
    with pytest.raises(AssertionError):
        PadActionSpaceV1(DummyAEC(spaces.__getitem__))


def test_aec_api():
    api_test(PadActionSpaceV1(DummyAEC(boxes)), num_cycles=5)


def test_parallel_api():
    parallel_api_test(PadActionSpaceParallelV1(DummyParallel(discrete)), num_cycles=5)
