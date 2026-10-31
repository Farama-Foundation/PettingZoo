"""Regression tests for final transitions retained during frame skipping."""

from __future__ import annotations

import numpy as np
import pytest
from gymnasium.spaces import Box, Dict

from pettingzoo.utils.wrappers import FrameSkipParallelV1
from test.frame_skip_test import CountingParallel


class ReusedTransitionParallel(CountingParallel):
    """Reuses a shared array and nested info object after an agent finishes."""

    def __init__(self, truncate=False):
        super().__init__(kill={1: "agent_1"})
        self.buffer = np.zeros(2, dtype=np.float32)
        self.info = {"nested": {"frame": 0}}
        self.truncate_agent = truncate

    def observation_space(self, agent):
        return Dict({"pixels": Box(0.0, np.inf, (2,), dtype=np.float32)})

    def reset(self, seed=None, options=None):
        observations, infos = super().reset(seed=seed, options=options)
        self.buffer[:] = 0
        return {a: {"pixels": self.buffer} for a in observations}, infos

    def step(self, actions):
        obs, rewards, terms, truncs, infos = super().step(actions)
        self.buffer[:] = self.num_steps
        self.info["nested"]["frame"] = self.num_steps
        if self.truncate_agent and terms.get("agent_1", False):
            terms["agent_1"] = False
            truncs["agent_1"] = True
        return (
            {a: {"pixels": self.buffer} for a in obs},
            rewards,
            terms,
            truncs,
            dict.fromkeys(infos, self.info),
        )


@pytest.mark.parametrize("truncate", [False, True])
def test_parallel_frame_skip_preserves_departed_agent_buffers(truncate):
    inner = ReusedTransitionParallel(truncate=truncate)
    env = FrameSkipParallelV1(inner, 3)
    env.reset()
    obs, rewards, terms, truncs, infos = env.step({"agent_0": 0, "agent_1": 0})
    np.testing.assert_array_equal(obs["agent_1"]["pixels"], [1, 1])
    assert infos["agent_1"] == {"nested": {"frame": 1}}
    np.testing.assert_array_equal(obs["agent_0"]["pixels"], [3, 3])
    assert infos["agent_0"] == {"nested": {"frame": 3}}
    assert rewards == {"agent_0": 3.0, "agent_1": 1.0}
    assert terms["agent_1"] is (not truncate)
    assert truncs["agent_1"] is truncate
    assert env.agents == ["agent_0"]
