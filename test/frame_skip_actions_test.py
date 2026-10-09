"""Regression tests for mutable controls replayed by frame skipping."""

from __future__ import annotations

import numpy as np
import pytest
from gymnasium.spaces import Box, Dict

from pettingzoo.utils.wrappers import FrameSkipParallelV1, FrameSkipV1
from test.frame_skip_test import CountingParallel, TurnAEC


class MutableActionAEC(TurnAEC):
    """Records nested controls before optionally mutating them in place."""

    def __init__(self, mutate=False):
        super().__init__()
        self.mutate = mutate
        self.controls = []

    def action_space(self, agent):
        return Dict({"motor": Box(-100.0, 100.0, (2,), dtype=np.float64)})

    def step(self, action):
        self.controls.append((self.agent_selection, action["motor"].copy()))
        if self.mutate:
            action["motor"][:] = -99
        super().step(0)


@pytest.mark.parametrize("mutate", [False, True])
def test_aec_frame_skip_snapshots_mutable_actions(mutate):
    inner = MutableActionAEC(mutate=mutate)
    env = FrameSkipV1(inner, 3)
    env.reset()
    action = {"motor": np.array([1.0, 2.0])}
    env.step(action)
    np.testing.assert_array_equal(action["motor"], [1.0, 2.0])
    # The caller reuses a control buffer for the next agent's turn.
    action["motor"][:] = [3.0, 4.0]
    env.step(action)
    for agent, received in inner.controls:
        expected = [1.0, 2.0] if agent == "agent_0" else [3.0, 4.0]
        np.testing.assert_array_equal(received, expected)
    assert len(inner.controls) == 6


class MutableActionParallel(CountingParallel):
    """Consumes nested controls in place, including a newly added agent's."""

    def __init__(self, add=None):
        super().__init__(add=add)
        self.controls = []

    def action_space(self, agent):
        return Dict({"motor": Box(-100.0, 100.0, (2,), dtype=np.float64)})

    def step(self, actions):
        controls = {}
        for agent, action in actions.items():
            controls[agent] = action["motor"].copy()
            action["motor"][:] = -99
        self.controls.append(controls)
        # Consuming the input dictionary must not remove the replayed actions.
        actions.clear()
        return super().step(dict.fromkeys(self.agents, 0))


@pytest.mark.parametrize("add_agent", [False, True])
def test_parallel_frame_skip_snapshots_mutable_actions(add_agent):
    inner = MutableActionParallel(add={1: "agent_2"} if add_agent else None)
    default = {"motor": np.array([5.0, 6.0])}
    env = FrameSkipParallelV1(inner, 3, default_action=default)
    env.reset()
    actions = {
        "agent_0": {"motor": np.array([1.0, 2.0])},
        "agent_1": {"motor": np.array([3.0, 4.0])},
    }
    env.step(actions)
    assert set(actions) == {"agent_0", "agent_1"}
    for controls in inner.controls:
        np.testing.assert_array_equal(controls["agent_0"], [1.0, 2.0])
        np.testing.assert_array_equal(controls["agent_1"], [3.0, 4.0])
    if add_agent:
        for controls in inner.controls[1:]:
            np.testing.assert_array_equal(controls["agent_2"], [5.0, 6.0])
    np.testing.assert_array_equal(default["motor"], [5.0, 6.0])
    np.testing.assert_array_equal(actions["agent_0"]["motor"], [1.0, 2.0])
    np.testing.assert_array_equal(actions["agent_1"]["motor"], [3.0, 4.0])
