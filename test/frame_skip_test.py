from __future__ import annotations

import functools

import numpy as np
import pytest
from gymnasium.spaces import Box, Discrete
from gymnasium.utils import seeding

from pettingzoo.butterfly import pistonball_v6
from pettingzoo.classic import tictactoe_v3
from pettingzoo.test import api_test, parallel_api_test
from pettingzoo.test.example_envs import (
    generated_agents_env_v0,
    generated_agents_parallel_v0,
)
from pettingzoo.utils.env import AECEnv, ParallelEnv
from pettingzoo.utils.wrappers import FrameSkipParallelV1, FrameSkipV1

OBS = np.zeros(2, dtype=np.float32)


@functools.cache
def obs_space(agent):
    return Box(low=0.0, high=1.0, shape=(2,), dtype=np.float32)


@functools.cache
def act_space(agent):
    return Discrete(100)


class TurnAEC(AECEnv):
    """Agents take turns. The acting agent gets reward 1, every other agent 10.

    ``done_at`` ends the episode for everyone after that many steps,
    ``kill`` maps a step count to an agent that terminates on that step, and
    ``add_at`` adds ``agent_2`` after that many steps.
    """

    metadata = {"render_modes": [], "name": "turn_aec"}

    def __init__(self, done_at=100, truncate=False, kill=None, add_at=None):
        super().__init__()
        self.possible_agents = ["agent_0", "agent_1", "agent_2"]
        self.done_at = done_at
        self.truncate = truncate
        self.kill = kill or {}
        self.add_at = add_at
        self.received = []

    def observation_space(self, agent):
        return obs_space(agent)

    def action_space(self, agent):
        return act_space(agent)

    def reset(self, seed=None, options=None):
        self.agents = ["agent_0", "agent_1"]
        self.rewards = dict.fromkeys(self.agents, 0.0)
        self._cumulative_rewards = dict.fromkeys(self.agents, 0.0)
        self.terminations = dict.fromkeys(self.agents, False)
        self.truncations = dict.fromkeys(self.agents, False)
        self.infos = {a: {} for a in self.agents}
        self.received = []
        self.num_steps = 0
        self.agent_selection = self.agents[0]

    def observe(self, agent):
        return OBS

    def step(self, action):
        agent = self.agent_selection
        if self.terminations[agent] or self.truncations[agent]:
            self._was_dead_step(action)
            return
        self.received.append((agent, action))
        self.num_steps += 1
        self._cumulative_rewards[agent] = 0.0
        self.rewards = {a: 1.0 if a == agent else 10.0 for a in self.agents}
        if self.num_steps == self.add_at:
            self.agents.append("agent_2")
            for d, v in [
                (self.rewards, 0.0),
                (self._cumulative_rewards, 0.0),
                (self.terminations, False),
                (self.truncations, False),
            ]:
                d["agent_2"] = v
            self.infos["agent_2"] = {}
        if self.num_steps in self.kill:
            self.terminations[self.kill[self.num_steps]] = True
        if self.num_steps >= self.done_at:
            flags = self.truncations if self.truncate else self.terminations
            for a in self.agents:
                flags[a] = True
        live = [
            a for a in self.agents if not (self.terminations[a] or self.truncations[a])
        ]
        if live:
            order = [a for a in self.agents if a in live]
            after = [
                a for a in order if self.agents.index(a) > self.agents.index(agent)
            ]
            self.agent_selection = (after or order)[0]
        self._accumulate_rewards()
        self._deads_step_first()

    def render(self):
        return None

    def close(self):
        pass


def play(env, actions):
    """Runs agent_iter, taking the next value of ``actions`` for each live turn."""
    actions = iter(actions)
    seen = []
    for agent in env.agent_iter():
        _, reward, termination, truncation, _ = env.last()
        seen.append((agent, reward, termination or truncation))
        env.step(None if termination or truncation else next(actions))
    return seen


def test_aec_repeats_action_and_keeps_turn_order():
    inner = TurnAEC()
    env = FrameSkipV1(inner, 3)
    env.reset()

    turns = []
    for action in [5, 6, 7, 8]:
        turns.append(env.agent_selection)
        env.step(action)

    assert turns == ["agent_0", "agent_1", "agent_0", "agent_1"]
    # Each action is used for three of its agent's turns.
    assert inner.received == [
        ("agent_0", 5),
        ("agent_1", 6),
        ("agent_0", 5),
        ("agent_1", 6),
        ("agent_0", 5),
        ("agent_1", 6),
        ("agent_0", 7),
        ("agent_1", 8),
        ("agent_0", 7),
        ("agent_1", 8),
        ("agent_0", 7),
        ("agent_1", 8),
    ]


def test_aec_accumulates_rewards_since_agent_last_acted():
    env = FrameSkipV1(TurnAEC(), 2)
    env.reset()

    env.step(5)  # agent_0 once
    assert env.agent_selection == "agent_1"
    assert env.rewards == {"agent_0": 1.0, "agent_1": 10.0}
    assert env.last()[1] == 10.0

    env.step(6)  # agent_1, agent_0, agent_1
    assert env.agent_selection == "agent_0"
    assert env.rewards == {"agent_0": 21.0, "agent_1": 12.0}
    # agent_0 got 1 + 10 + 1 + 10 since it last acted.
    assert env.last()[1] == 22.0
    assert env._cumulative_rewards == {"agent_0": 22.0, "agent_1": 12.0}


def test_aec_num_frames_one_is_unchanged():
    plain, wrapped = TurnAEC(done_at=7), FrameSkipV1(TurnAEC(done_at=7), 1)
    plain.reset()
    wrapped.reset()
    assert play(wrapped, range(10, 100)) == play(plain, range(10, 100))
    assert wrapped.unwrapped.received == plain.received


@pytest.mark.parametrize("truncate", [False, True])
def test_aec_stops_replaying_when_episode_ends(truncate):
    inner = TurnAEC(done_at=4, truncate=truncate)
    env = FrameSkipV1(inner, 3)
    env.reset()

    seen = play(env, [5, 6, 7])

    assert inner.received == [
        ("agent_0", 5),
        ("agent_1", 6),
        ("agent_0", 5),
        ("agent_1", 6),
    ]
    # Both agents get their dead step with the rewards since they last acted.
    assert seen == [
        ("agent_0", 0.0, False),
        ("agent_1", 10.0, False),
        ("agent_0", 22.0, True),
        ("agent_1", 12.0, True),
    ]
    assert env.agents == []


def test_aec_agent_removed_while_replaying():
    inner = TurnAEC(done_at=8, kill={3: "agent_1"})
    env = FrameSkipV1(inner, 3)
    env.reset()

    seen = play(env, range(5, 50))

    # agent_1 terminates on the 3rd step, its dead step comes back to the
    # caller, and agent_0's replay continues afterwards.
    assert seen[:4] == [
        ("agent_0", 0.0, False),
        ("agent_1", 10.0, False),
        ("agent_1", 11.0, True),
        ("agent_0", 13.0, False),
    ]
    assert inner.received[:4] == [
        ("agent_0", 5),
        ("agent_1", 6),
        ("agent_0", 5),
        ("agent_0", 5),
    ]
    assert "agent_1" not in env.agents
    assert set(env.rewards) == set(env._cumulative_rewards) == set(env.agents)


def test_aec_added_agent_gets_its_first_action_from_caller():
    inner = TurnAEC(add_at=2)
    env = FrameSkipV1(inner, 2)
    env.reset()

    env.step(5)
    env.step(6)  # agent_1, then agent_2 is added and has no action yet
    assert env.agents == ["agent_0", "agent_1", "agent_2"]
    assert env.agent_selection == "agent_2"
    assert env.last()[1] == 0.0
    env.step(7)

    assert inner.received[:4] == [
        ("agent_0", 5),
        ("agent_1", 6),
        ("agent_2", 7),
        ("agent_0", 5),
    ]


def test_aec_reset_clears_pending_actions_and_rewards():
    inner = TurnAEC()
    env = FrameSkipV1(inner, 3)
    env.reset()
    env.step(5)
    env.step(6)

    env.reset()
    assert env.rewards == {"agent_0": 0.0, "agent_1": 0.0}
    assert env._cumulative_rewards == {"agent_0": 0.0, "agent_1": 0.0}
    env.step(7)
    # agent_1's pending action from before the reset is gone.
    assert env.agent_selection == "agent_1"
    assert inner.received == [("agent_0", 7)]


@pytest.mark.parametrize("num_frames", [0, -1, 1.5, True, (1, 2), None])
def test_aec_rejects_invalid_num_frames(num_frames):
    with pytest.raises(AssertionError):
        FrameSkipV1(TurnAEC(), num_frames)


def test_aec_rejects_parallel_env():
    with pytest.raises(AssertionError):
        FrameSkipV1(CountingParallel(), 2)


@pytest.mark.parametrize(
    "make_env",
    [
        tictactoe_v3.env,
        lambda: pistonball_v6.env(continuous=False),
        generated_agents_env_v0.env,
        lambda: TurnAEC(done_at=30, kill={7: "agent_1"}, add_at=3),
    ],
)
@pytest.mark.parametrize("num_frames", [1, 3])
def test_aec_api(make_env, num_frames):
    api_test(FrameSkipV1(make_env(), num_frames), num_cycles=200)


class CountingParallel(ParallelEnv):
    """Every live agent gets reward 1 per step.

    ``kill`` maps a step count to an agent that terminates on that step,
    ``add`` maps a step count to an agent added on it, and ``done_at`` ends the
    episode for everyone.
    """

    metadata = {"render_modes": [], "name": "counting_parallel"}

    def __init__(self, done_at=100, truncate=False, kill=None, add=None):
        self.possible_agents = ["agent_0", "agent_1", "agent_2"]
        self.done_at = done_at
        self.truncate = truncate
        self.kill = kill or {}
        self.add = add or {}
        self.received = []
        self.np_random, _ = seeding.np_random(None)

    def observation_space(self, agent):
        return obs_space(agent)

    def action_space(self, agent):
        return act_space(agent)

    def reset(self, seed=None, options=None):
        self.np_random, _ = seeding.np_random(seed)
        self.agents = ["agent_0", "agent_1"]
        self.num_steps = 0
        self.received = []
        return dict.fromkeys(self.agents, OBS), {a: {} for a in self.agents}

    def step(self, actions):
        self.received.append(dict(actions))
        self.num_steps += 1
        agents = list(self.agents)
        if self.num_steps in self.add:
            agents.append(self.add[self.num_steps])
        obs = {a: np.full(2, self.num_steps / 100, dtype=np.float32) for a in agents}
        rewards = dict.fromkeys(agents, 1.0)
        done = self.num_steps >= self.done_at
        terminations = {
            a: (done and not self.truncate) or self.kill.get(self.num_steps) == a
            for a in agents
        }
        truncations = dict.fromkeys(agents, done and self.truncate)
        infos = {a: {"step": self.num_steps} for a in agents}
        self.agents = [a for a in agents if not (terminations[a] or truncations[a])]
        return obs, rewards, terminations, truncations, infos

    def render(self):
        return None

    def close(self):
        pass


def test_parallel_repeats_actions_and_sums_rewards():
    inner = CountingParallel()
    env = FrameSkipParallelV1(inner, 3)
    env.reset()

    obs, rewards, terminations, truncations, infos = env.step(
        {"agent_0": 4, "agent_1": 5}
    )

    assert inner.received == [{"agent_0": 4, "agent_1": 5}] * 3
    assert rewards == {"agent_0": 3.0, "agent_1": 3.0}
    assert terminations == truncations == {"agent_0": False, "agent_1": False}
    assert infos == {"agent_0": {"step": 3}, "agent_1": {"step": 3}}
    np.testing.assert_array_equal(obs["agent_0"], np.full(2, 0.03, np.float32))


@pytest.mark.parametrize("truncate", [False, True])
def test_parallel_stops_when_episode_ends(truncate):
    inner = CountingParallel(done_at=2, truncate=truncate)
    env = FrameSkipParallelV1(inner, 5)
    env.reset()

    _, rewards, terminations, truncations, _ = env.step({"agent_0": 4, "agent_1": 5})

    assert len(inner.received) == 2
    assert rewards == {"agent_0": 2.0, "agent_1": 2.0}
    flags = truncations if truncate else terminations
    assert flags == {"agent_0": True, "agent_1": True}
    assert env.agents == []


def test_parallel_agent_removed_partway_keeps_final_transition():
    inner = CountingParallel(kill={1: "agent_1"})
    env = FrameSkipParallelV1(inner, 3)
    env.reset()

    obs, rewards, terminations, _, infos = env.step({"agent_0": 4, "agent_1": 5})

    assert inner.received == [
        {"agent_0": 4, "agent_1": 5},
        {"agent_0": 4},
        {"agent_0": 4},
    ]
    assert rewards == {"agent_0": 3.0, "agent_1": 1.0}
    assert terminations == {"agent_0": False, "agent_1": True}
    assert infos["agent_1"] == {"step": 1}
    np.testing.assert_array_equal(obs["agent_1"], np.full(2, 0.01, np.float32))


def test_parallel_added_agent_uses_default_action():
    inner = CountingParallel(add={1: "agent_2"})
    env = FrameSkipParallelV1(inner, 3, default_action=0)
    env.reset()

    _, rewards, _, _, _ = env.step({"agent_0": 4, "agent_1": 5})

    assert inner.received[1:] == [{"agent_0": 4, "agent_1": 5, "agent_2": 0}] * 2
    assert rewards == {"agent_0": 3.0, "agent_1": 3.0, "agent_2": 3.0}
    assert env.agents == ["agent_0", "agent_1", "agent_2"]


def test_parallel_added_agent_without_default_action_raises():
    env = FrameSkipParallelV1(CountingParallel(add={1: "agent_2"}), 3)
    env.reset()
    with pytest.raises(ValueError, match="default_action"):
        env.step({"agent_0": 4, "agent_1": 5})


def test_parallel_drops_agent_added_and_removed_within_one_step():
    inner = CountingParallel(add={1: "agent_2"}, kill={2: "agent_2"})
    env = FrameSkipParallelV1(inner, 3, default_action=0)
    env.reset()

    results = env.step({"agent_0": 4, "agent_1": 5})

    assert len(inner.received) == 3
    for result in results:
        assert set(result) == {"agent_0", "agent_1"}


def test_parallel_random_num_frames_uses_env_rng():
    def step_counts(seed):
        inner = CountingParallel()
        env = FrameSkipParallelV1(inner, (1, 4))
        env.reset(seed=seed)
        counts = []
        for _ in range(20):
            before = len(inner.received)
            env.step({"agent_0": 4, "agent_1": 5})
            counts.append(len(inner.received) - before)
        return counts

    counts = step_counts(42)
    assert counts == step_counts(42)
    assert set(counts) == {1, 2, 3, 4}


@pytest.mark.parametrize(
    "num_frames", [0, -2, 2.0, False, (0, 2), (3, 2), (1, 2, 3), (1, 2.5), None]
)
def test_parallel_rejects_invalid_num_frames(num_frames):
    with pytest.raises(AssertionError):
        FrameSkipParallelV1(CountingParallel(), num_frames)


@pytest.mark.parametrize(
    "make_env",
    [
        lambda: pistonball_v6.parallel_env(continuous=False),
        generated_agents_parallel_v0.parallel_env,
        lambda: CountingParallel(done_at=12, kill={3: "agent_1"}, add={5: "agent_2"}),
    ],
)
@pytest.mark.parametrize("num_frames", [1, 3, (1, 3)])
def test_parallel_api(make_env, num_frames):
    parallel_api_test(
        FrameSkipParallelV1(make_env(), num_frames, default_action=0),
        num_cycles=200,
    )
