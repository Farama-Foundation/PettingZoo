"""Tests for the seed test helpers themselves (``pettingzoo/test/seed_test.py``)."""

from __future__ import annotations

import random

import numpy as np
import pytest
from gymnasium.spaces import Box, Discrete

from pettingzoo import ParallelEnv
from pettingzoo.test import parallel_seed_test

NUM_AGENTS = 2
NUM_CYCLES = 10
MAX_STEPS = 100


class DivergingParallelEnv(ParallelEnv):
    """A parallel env that is deterministic until ``diverge_after`` steps have run.

    From then on its observations are drawn from the unseeded global ``random``
    module, so two instances built with the same seed produce different
    trajectories. With ``diverge_after=None`` the env never diverges.
    """

    metadata = {"render_modes": [], "name": "diverging_parallel_v0"}

    def __init__(self, diverge_after: int | None = None):
        super().__init__()
        self.diverge_after = diverge_after
        self.possible_agents = [f"player_{i}" for i in range(NUM_AGENTS)]
        self.agents = []
        self.num_steps = 0
        # Spaces must be created once so that seeding them actually sticks.
        self._observation_spaces = {
            agent: Box(low=0.0, high=1.0, shape=(1,), dtype=np.float32)
            for agent in self.possible_agents
        }
        self._action_spaces = {agent: Discrete(2) for agent in self.possible_agents}

    def observation_space(self, agent):
        return self._observation_spaces[agent]

    def action_space(self, agent):
        return self._action_spaces[agent]

    def _observe(self, agent):
        if self.diverge_after is not None and self.num_steps > self.diverge_after:
            value = random.random()  # deliberately unseeded
        else:
            value = self.num_steps / MAX_STEPS
        return np.array([value], dtype=np.float32)

    def reset(self, seed=None, options=None):
        self.agents = list(self.possible_agents)
        self.num_steps = 0
        observations = {agent: self._observe(agent) for agent in self.agents}
        return observations, {agent: {} for agent in self.agents}

    def step(self, actions):
        self.num_steps += 1
        truncated = self.num_steps >= MAX_STEPS
        observations = {agent: self._observe(agent) for agent in self.agents}
        rewards = dict.fromkeys(self.agents, 0)
        terminations = dict.fromkeys(self.agents, False)
        truncations = dict.fromkeys(self.agents, truncated)
        infos = {agent: {} for agent in self.agents}
        if truncated:
            self.agents = []
        return observations, rewards, terminations, truncations, infos

    def render(self):
        pass

    def close(self):
        pass


def test_parallel_seed_test_accepts_deterministic_env():
    parallel_seed_test(DivergingParallelEnv, num_cycles=NUM_CYCLES)


@pytest.mark.parametrize("diverge_after", [1, 3, 5])
def test_parallel_seed_test_detects_late_divergence(diverge_after):
    """An env that only diverges after a few steps must still fail the seed test."""
    with pytest.raises(AssertionError, match="Incorrect observations"):
        parallel_seed_test(
            lambda: DivergingParallelEnv(diverge_after=diverge_after),
            num_cycles=NUM_CYCLES,
        )


def test_parallel_seed_test_runs_more_than_one_step():
    envs = []

    def env_fn():
        env = DivergingParallelEnv()
        envs.append(env)
        return env

    parallel_seed_test(env_fn, num_cycles=NUM_CYCLES)

    assert envs, "no environment was constructed"
    for env in envs:
        assert env.num_steps >= NUM_CYCLES, (
            f"seed test only ran {env.num_steps} steps for num_cycles={NUM_CYCLES}"
        )
