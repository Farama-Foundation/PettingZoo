from __future__ import annotations

import functools

import numpy as np
import pytest
from gymnasium.spaces import Box, Discrete

from pettingzoo.test import api_test, parallel_api_test
from pettingzoo.utils.env import AECEnv, ParallelEnv
from pettingzoo.utils.wrappers import ClipRewardParallelV1, ClipRewardV1

AGENTS = ["agent_0", "agent_1"]
OBS = np.array([0.25, 0.75], dtype=np.float32)
RAW_REWARD = 10.0


@functools.cache
def obs_space(agent):
    return Box(low=0.0, high=1.0, shape=(2,), dtype=np.float32)


class DummyAEC(AECEnv):
    """Gives RAW_REWARD to the agent that just stepped."""

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
        return OBS

    def step(self, action):
        if (
            self.terminations[self.agent_selection]
            or self.truncations[self.agent_selection]
        ):
            self._was_dead_step(action)
            return
        self._step_count += 1
        self._clear_rewards()
        self.rewards[self.agent_selection] = RAW_REWARD
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
        return dict.fromkeys(self.agents, OBS), {a: {} for a in self.agents}

    def step(self, actions):
        self._step_count += 1
        done = self._step_count >= 8
        obs = dict.fromkeys(self.agents, OBS)
        rewards = dict.fromkeys(self.agents, RAW_REWARD)
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


class NegativeAEC(DummyAEC):
    def step(self, action):
        if (
            self.terminations[self.agent_selection]
            or self.truncations[self.agent_selection]
        ):
            self._was_dead_step(action)
            return
        self._step_count += 1
        self._clear_rewards()
        self.rewards[self.agent_selection] = -RAW_REWARD
        if self._step_count >= 8:
            self.terminations = dict.fromkeys(self.agents, True)
        self._idx = (self._idx + 1) % len(self.agents)
        self.agent_selection = self.agents[self._idx]
        self._accumulate_rewards()


def test_aec_clips_step_reward():
    env = ClipRewardV1(DummyAEC(), min_reward=-1, max_reward=1)
    env.reset(seed=0)
    env.step(0)
    assert env.rewards["agent_0"] == 1.0
    assert env.rewards["agent_1"] == 0.0


def test_aec_last_reports_clipped_reward():
    env = ClipRewardV1(DummyAEC(), min_reward=-1, max_reward=1)
    env.reset(seed=0)
    env.step(0)
    env.step(0)
    # agent_0 has just become current again; last() is its clipped step.
    _, cumulative, _, _, _ = env.last()
    assert cumulative == 1.0


def test_aec_clips_negative_rewards():
    env = ClipRewardV1(NegativeAEC(), min_reward=-1, max_reward=1)
    env.reset(seed=0)
    env.step(0)
    assert env.rewards["agent_0"] == -1.0


def test_aec_in_range_reward_is_unchanged():
    env = ClipRewardV1(DummyAEC(), min_reward=-20, max_reward=20)
    env.reset(seed=0)
    env.step(0)
    assert env.rewards["agent_0"] == RAW_REWARD


def test_parallel_clips_step_reward():
    env = ClipRewardParallelV1(DummyParallel(), min_reward=-1, max_reward=1)
    env.reset(seed=0)
    _, rewards, _, _, _ = env.step(dict.fromkeys(AGENTS, 0))
    assert rewards == {"agent_0": 1.0, "agent_1": 1.0}


def test_parallel_in_range_reward_is_unchanged():
    env = ClipRewardParallelV1(DummyParallel(), min_reward=-20, max_reward=20)
    env.reset(seed=0)
    _, rewards, _, _, _ = env.step(dict.fromkeys(AGENTS, 0))
    assert rewards == {"agent_0": RAW_REWARD, "agent_1": RAW_REWARD}


def test_defaults_are_minus_one_and_one():
    env = ClipRewardV1(DummyAEC())
    env.reset(seed=0)
    env.step(0)
    assert env.rewards["agent_0"] == 1.0
    assert env.min_reward == -1
    assert env.max_reward == 1


def test_inverted_bounds_raise():
    with pytest.raises(AssertionError, match="min_reward"):
        ClipRewardV1(DummyAEC(), min_reward=1, max_reward=-1)
    with pytest.raises(AssertionError, match="min_reward"):
        ClipRewardParallelV1(DummyParallel(), min_reward=1, max_reward=-1)


def test_rejects_parallel_env():
    with pytest.raises(AssertionError, match="ClipRewardParallelV1"):
        ClipRewardV1(DummyParallel())


def test_str():
    assert str(ClipRewardV1(DummyAEC())).startswith("ClipRewardV1<")
    assert str(ClipRewardParallelV1(DummyParallel())).startswith(
        "ClipRewardParallelV1<"
    )


def test_aec_api():
    api_test(ClipRewardV1(DummyAEC()), num_cycles=5)


def test_parallel_api():
    parallel_api_test(ClipRewardParallelV1(DummyParallel()), num_cycles=10)
