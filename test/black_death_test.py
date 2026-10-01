from __future__ import annotations

import functools

import numpy as np
import pytest
from gymnasium.spaces import Box, Discrete

from pettingzoo.butterfly import knights_archers_zombies_v11
from pettingzoo.test import parallel_api_test
from pettingzoo.utils.env import ParallelEnv
from pettingzoo.utils.wrappers import BlackDeathParallelV4

from .scale_action_test import DummyParallel

AGENTS = ["agent_0", "agent_1", "agent_2"]
OBS_SPACE = Box(low=-1.0, high=1.0, shape=(2,), dtype=np.float32)
OBS = np.array([0.5, -0.5], dtype=np.float32)


class StaggeredParallel(ParallelEnv):
    """``agent_0`` terminates at step 2 with a reward of -5, ``agent_1`` is
    truncated at step 3, and ``agent_2`` ends the episode at step 5, either by
    termination or by truncation."""

    metadata = {"render_modes": [], "name": "staggered_parallel"}

    def __init__(self, end="truncation", obs_space=OBS_SPACE):
        super().__init__()
        self.possible_agents = list(AGENTS)
        self._end = end
        self._obs_space = obs_space
        self.received = []

    def observation_space(self, agent):
        return self._obs_space

    @functools.cache
    def action_space(self, agent):
        return Discrete(2)

    def reset(self, seed=None, options=None):
        self.agents = list(self.possible_agents)
        self.received = []
        self.reset_options = options
        self._t = 0
        return dict.fromkeys(self.agents, OBS), {a: {} for a in self.agents}

    def step(self, actions):
        self.received.append(dict(actions))
        self._t += 1
        obs = dict.fromkeys(self.agents, OBS)
        rewards = dict.fromkeys(self.agents, 1.0)
        terminations = dict.fromkeys(self.agents, False)
        truncations = dict.fromkeys(self.agents, False)
        infos = {a: {"t": self._t} for a in self.agents}
        if self._t == 2:
            rewards["agent_0"] = -5.0
            terminations["agent_0"] = True
        if self._t == 3:
            truncations["agent_1"] = True
        if self._t == 5:
            flags = terminations if self._end == "termination" else truncations
            flags["agent_2"] = True
        self.agents = [
            a for a in self.agents if not (terminations[a] or truncations[a])
        ]
        return obs, rewards, terminations, truncations, infos

    def render(self):
        return None

    def close(self):
        pass


def _run(env):
    env.reset(seed=0)
    steps = []
    while env.agents:
        steps.append(env.step(dict.fromkeys(env.agents, 1)))
    return steps


def test_departed_agents_stay_with_black_observations():
    env = BlackDeathParallelV4(StaggeredParallel())
    env.reset(seed=0)
    env.step(dict.fromkeys(env.agents, 1))

    # step 2: agent_0 leaves; its real reward and info are kept, flags are False
    obs, rewards, terms, truncs, infos = env.step(dict.fromkeys(env.agents, 1))
    assert env.agents == AGENTS
    np.testing.assert_array_equal(obs["agent_0"], OBS)
    assert rewards["agent_0"] == -5.0
    assert infos["agent_0"] == {"t": 2}
    assert terms == dict.fromkeys(AGENTS, False)
    assert truncs == dict.fromkeys(AGENTS, False)

    # step 3: agent_0 gets zeros, agent_1 leaves by truncation
    obs, rewards, terms, truncs, infos = env.step(dict.fromkeys(env.agents, 1))
    assert env.agents == AGENTS
    assert obs["agent_0"].dtype == OBS_SPACE.dtype
    np.testing.assert_array_equal(obs["agent_0"], np.zeros(2, dtype=np.float32))
    assert OBS_SPACE.contains(obs["agent_0"])
    assert rewards["agent_0"] == 0.0
    assert infos["agent_0"] == {}
    assert rewards["agent_1"] == 1.0
    assert terms == dict.fromkeys(AGENTS, False)
    assert truncs == dict.fromkeys(AGENTS, False)


def test_actions_for_departed_agents_are_ignored():
    inner = StaggeredParallel()
    env = BlackDeathParallelV4(inner)
    _run(env)
    assert [set(actions) for actions in inner.received] == [
        set(AGENTS),
        set(AGENTS),
        {"agent_1", "agent_2"},
        {"agent_2"},
        {"agent_2"},
    ]


@pytest.mark.parametrize("end", ["termination", "truncation"])
def test_episode_end_keeps_each_agents_own_flags(end):
    env = BlackDeathParallelV4(StaggeredParallel(end))
    steps = _run(env)
    assert len(steps) == 5
    for _, _, terms, truncs, _ in steps[:-1]:
        assert not any(terms.values())
        assert not any(truncs.values())

    obs, rewards, terms, truncs, _ = steps[-1]
    assert env.agents == []
    assert set(obs) == set(AGENTS)
    assert rewards == {"agent_0": 0.0, "agent_1": 0.0, "agent_2": 1.0}
    assert terms["agent_0"] and not truncs["agent_0"]
    assert truncs["agent_1"] and not terms["agent_1"]
    assert terms["agent_2"] == (end == "termination")
    assert truncs["agent_2"] == (end == "truncation")


def test_episode_ending_for_all_agents_at_once():
    env = BlackDeathParallelV4(DummyParallel())
    env.reset(seed=0)
    for _ in range(7):
        _, _, terms, truncs, _ = env.step(dict.fromkeys(env.agents, None))
        assert not any(terms.values()) and not any(truncs.values())
    _, _, terms, truncs, _ = env.step(dict.fromkeys(env.agents, None))
    assert terms == {"agent_0": True, "agent_1": True}
    assert truncs == {"agent_0": False, "agent_1": False}
    assert env.agents == []


def test_reset_starts_a_fresh_agent_set():
    inner = StaggeredParallel()
    env = BlackDeathParallelV4(inner)
    _run(env)
    assert env.agents == []

    obs, infos = env.reset(seed=1, options={"x": 1})
    assert env.agents == AGENTS
    assert set(obs) == set(AGENTS)
    assert inner.reset_options == {"x": 1}

    # agent_0 is active again, so its action is forwarded
    env.step(dict.fromkeys(env.agents, 1))
    assert set(inner.received[-1]) == set(AGENTS)


def test_non_box_observation_space_is_rejected():
    env = BlackDeathParallelV4(StaggeredParallel(obs_space=Discrete(3)))
    with pytest.raises(ValueError, match="agent_0"):
        env.reset()


def test_box_excluding_zero_is_rejected():
    space = Box(low=1.0, high=2.0, shape=(2,), dtype=np.float32)
    env = BlackDeathParallelV4(StaggeredParallel(obs_space=space))
    with pytest.raises(ValueError, match="zero is outside"):
        env.reset()


@pytest.mark.parametrize("end", ["termination", "truncation"])
def test_parallel_api_staggered(end):
    parallel_api_test(BlackDeathParallelV4(StaggeredParallel(end)), num_cycles=10)


def test_parallel_api_dummy():
    parallel_api_test(BlackDeathParallelV4(DummyParallel()), num_cycles=10)


def test_parallel_api_knights_archers_zombies():
    env = knights_archers_zombies_v11.parallel_env(max_cycles=300)
    parallel_api_test(BlackDeathParallelV4(env), num_cycles=1000)
