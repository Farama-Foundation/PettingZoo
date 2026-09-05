from __future__ import annotations

import functools

import numpy as np
import pytest
from gymnasium.spaces import Box, Discrete
from gymnasium.utils import seeding

from pettingzoo.test import api_test, parallel_api_test
from pettingzoo.utils.env import AECEnv, ParallelEnv
from pettingzoo.utils.wrappers import (
    OrderEnforcingWrapper,
    StickyActionParallelV1,
    StickyActionV1,
)

AGENTS = ["agent_0", "agent_1"]

# Close enough to 1 that a non-repeat is a one-in-a-billion event.
ALWAYS = 1.0 - 1e-9

# Large enough that a test can submit a different action on every step of its
# window. Reusing an action value would let a repeat pass for a pass-through.
N_ACTIONS = 64

OBS = np.array([0.25, 0.75], dtype=np.float32)


@functools.cache
def obs_space(agent):
    return Box(low=0.0, high=1.0, shape=(2,), dtype=np.float32)


class DummyAEC(AECEnv):
    """Records the action each agent was actually stepped with."""

    metadata = {"render_modes": [], "name": "dummy_aec"}

    def __init__(self):
        super().__init__()
        self.possible_agents = list(AGENTS)
        self.received = []
        self.seen_seed = "unset"

    def observation_space(self, agent):
        return obs_space(agent)

    @functools.cache
    def action_space(self, agent):
        return Discrete(N_ACTIONS)

    def reset(self, seed=None, options=None):
        self.seen_seed = seed
        self.agents = list(self.possible_agents)
        self.rewards = dict.fromkeys(self.agents, 0.0)
        self._cumulative_rewards = dict.fromkeys(self.agents, 0.0)
        self.terminations = dict.fromkeys(self.agents, False)
        self.truncations = dict.fromkeys(self.agents, False)
        self.infos = {a: {} for a in self.agents}
        self.received = []
        self._idx = 0
        self._step_count = 0
        self.agent_selection = self.agents[0]

    def observe(self, agent):
        return OBS

    def step(self, action):
        self.received.append((self.agent_selection, action))
        self._step_count += 1
        self._cumulative_rewards[self.agent_selection] = 0.0
        self.rewards = dict.fromkeys(self.agents, 0.0)
        if self._step_count >= 20:
            self.terminations = dict.fromkeys(self.agents, True)
        self._idx = (self._idx + 1) % len(self.agents)
        self.agent_selection = self.agents[self._idx]
        self._accumulate_rewards()

    def render(self):
        return None

    def close(self):
        pass


class DyingAEC(AECEnv):
    """AEC env where agent_1 dies first, so both agents take a real dead step."""

    metadata = {"render_modes": [], "name": "dying_aec"}

    def __init__(self):
        super().__init__()
        self.possible_agents = list(AGENTS)
        self.received = []

    def observation_space(self, agent):
        return obs_space(agent)

    @functools.cache
    def action_space(self, agent):
        return Discrete(N_ACTIONS)

    def reset(self, seed=None, options=None):
        self.agents = list(self.possible_agents)
        self.rewards = dict.fromkeys(self.agents, 0.0)
        self._cumulative_rewards = dict.fromkeys(self.agents, 0.0)
        self.terminations = dict.fromkeys(self.agents, False)
        self.truncations = dict.fromkeys(self.agents, False)
        self.infos = {a: {} for a in self.agents}
        self.received = []
        self._step_count = 0
        self.agent_selection = self.agents[0]

    def observe(self, agent):
        return OBS

    def step(self, action):
        self.received.append((self.agent_selection, action))
        if (
            self.terminations[self.agent_selection]
            or self.truncations[self.agent_selection]
        ):
            self._was_dead_step(action)
            return

        self._step_count += 1
        self._clear_rewards()
        # `==`, not `>=`: a removed agent must not be given a termination again.
        if self._step_count == 2:
            self.terminations["agent_1"] = True
        if self._step_count == 4:
            self.terminations["agent_0"] = True

        idx = self.agents.index(self.agent_selection)
        self.agent_selection = self.agents[(idx + 1) % len(self.agents)]
        self._accumulate_rewards()
        self.agent_selection = self._deads_step_first()

    def render(self):
        return None

    def close(self):
        pass


class DummyParallel(ParallelEnv):
    """Records the actions dict each step was actually called with."""

    metadata = {"render_modes": [], "name": "dummy_parallel"}

    def __init__(self):
        super().__init__()
        self.possible_agents = list(AGENTS)
        self.received = []
        self.seen_seed = "unset"

    def observation_space(self, agent):
        return obs_space(agent)

    @functools.cache
    def action_space(self, agent):
        return Discrete(N_ACTIONS)

    def reset(self, seed=None, options=None):
        self.seen_seed = seed
        self.agents = list(self.possible_agents)
        self.received = []
        self._step_count = 0
        return dict.fromkeys(self.agents, OBS), {a: {} for a in self.agents}

    def step(self, actions):
        self.received.append(dict(actions))
        self._step_count += 1
        done = self._step_count >= 40
        obs = dict.fromkeys(self.agents, OBS)
        rewards = dict.fromkeys(self.agents, 0.0)
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


class DyingParallel(DummyParallel):
    """agent_1 terminates after the first step, then rejoins for the third."""

    metadata = {"render_modes": [], "name": "dying_parallel"}

    def step(self, actions):
        self.received.append(dict(actions))
        self._step_count += 1
        acting = list(self.agents)
        terminations = dict.fromkeys(acting, False)
        truncations = dict.fromkeys(acting, False)
        if self._step_count == 1:
            terminations["agent_1"] = True
            self.agents = ["agent_0"]
        elif self._step_count == 2:
            self.agents = list(AGENTS)
        obs = dict.fromkeys(self.agents, OBS)
        rewards = dict.fromkeys(acting, 0.0)
        infos = {a: {} for a in acting}
        return obs, rewards, terminations, truncations, infos


class BoxActionParallel(ParallelEnv):
    """One agent with a Box action space, optionally normalising the action in place."""

    metadata = {"render_modes": [], "name": "box_action_parallel"}

    def __init__(self, mutate=False):
        super().__init__()
        self.possible_agents = ["agent_0"]
        self.received = []
        self.mutate = mutate

    def observation_space(self, agent):
        return obs_space(agent)

    @functools.cache
    def action_space(self, agent):
        return Box(low=-1.0, high=1.0, shape=(2,), dtype=np.float32)

    def reset(self, seed=None, options=None):
        self.agents = list(self.possible_agents)
        self.received = []
        return {"agent_0": OBS}, {"agent_0": {}}

    def step(self, actions):
        self.received.append(actions["agent_0"].copy())
        if self.mutate:
            actions["agent_0"][:] = 0.0
        return (
            {"agent_0": OBS},
            {"agent_0": 0.0},
            {"agent_0": False},
            {"agent_0": False},
            {"agent_0": {}},
        )

    def render(self):
        return None

    def close(self):
        pass


class NoisyParallel(ParallelEnv):
    """One agent, one uniform of its own transition noise per step.

    Seeded the way PettingZoo environments normally seed themselves, so it shares
    a seed with the wrapper wrapping it.
    """

    metadata = {"render_modes": [], "name": "noisy_parallel"}

    def __init__(self):
        super().__init__()
        self.possible_agents = ["agent_0"]
        self.received = []
        self.noise = []

    def observation_space(self, agent):
        return obs_space(agent)

    @functools.cache
    def action_space(self, agent):
        return Discrete(N_ACTIONS)

    def reset(self, seed=None, options=None):
        self.np_random, _ = seeding.np_random(seed)
        self.agents = list(self.possible_agents)
        self.received = []
        self.noise = []
        return {"agent_0": OBS}, {"agent_0": {}}

    def step(self, actions):
        self.received.append(actions["agent_0"])
        self.noise.append(self.np_random.uniform())
        return (
            {"agent_0": OBS},
            {"agent_0": 0.0},
            {"agent_0": False},
            {"agent_0": False},
            {"agent_0": {}},
        )

    def render(self):
        return None

    def close(self):
        pass


def aec_actions_for(env, agent):
    """Actions the inner AEC env saw for one agent."""
    return [action for who, action in env.received if who == agent]


@pytest.mark.parametrize("probability", [0.0, 0.5, ALWAYS])
def test_aec_first_action_is_never_repeated(probability):
    inner = DummyAEC()
    env = StickyActionV1(inner, repeat_action_probability=probability)
    env.reset(seed=0)
    env.step(7)
    assert inner.received == [("agent_0", 7)]


@pytest.mark.parametrize("probability", [0.0, 0.5, ALWAYS])
def test_parallel_first_action_is_never_repeated(probability):
    inner = DummyParallel()
    env = StickyActionParallelV1(inner, repeat_action_probability=probability)
    env.reset(seed=0)
    env.step({"agent_0": 7, "agent_1": 3})
    assert inner.received == [{"agent_0": 7, "agent_1": 3}]


def test_aec_zero_probability_never_repeats():
    inner = DummyAEC()
    env = StickyActionV1(inner, repeat_action_probability=0.0)
    env.reset(seed=0)
    for action in range(8):
        env.step(action)
    assert [action for _, action in inner.received] == list(range(8))


def test_parallel_zero_probability_never_repeats():
    inner = DummyParallel()
    env = StickyActionParallelV1(inner, repeat_action_probability=0.0)
    env.reset(seed=0)
    for action in range(8):
        env.step({"agent_0": action, "agent_1": action + 32})
    assert inner.received == [
        {"agent_0": action, "agent_1": action + 32} for action in range(8)
    ]


def test_aec_high_probability_repeats_after_the_first_action():
    inner = DummyAEC()
    env = StickyActionV1(inner, repeat_action_probability=ALWAYS)
    env.reset(seed=0)
    for action in range(8):
        env.step(action)
    # agent_0 first sees 0, agent_1 first sees 1, then both stay stuck.
    assert aec_actions_for(inner, "agent_0") == [0, 0, 0, 0]
    assert aec_actions_for(inner, "agent_1") == [1, 1, 1, 1]


def test_parallel_high_probability_repeats_after_the_first_action():
    inner = DummyParallel()
    env = StickyActionParallelV1(inner, repeat_action_probability=ALWAYS)
    env.reset(seed=0)
    for action in range(8):
        env.step({"agent_0": action, "agent_1": 63 - action})
    assert inner.received == [{"agent_0": 0, "agent_1": 63}] * 8


def test_parallel_previous_actions_are_per_agent():
    inner = DummyParallel()
    env = StickyActionParallelV1(inner, repeat_action_probability=ALWAYS)
    env.reset(seed=0)
    env.step({"agent_0": 5, "agent_1": 3})
    env.step({"agent_0": 9, "agent_1": 7})
    # Each agent falls back to its own previous action, not the other agent's.
    assert inner.received == [
        {"agent_0": 5, "agent_1": 3},
        {"agent_0": 5, "agent_1": 3},
    ]


def test_aec_previous_actions_are_per_agent():
    inner = DummyAEC()
    env = StickyActionV1(inner, repeat_action_probability=ALWAYS)
    env.reset(seed=0)
    for action in [5, 3, 9, 7]:
        env.step(action)
    assert inner.received == [
        ("agent_0", 5),
        ("agent_1", 3),
        ("agent_0", 5),
        ("agent_1", 3),
    ]


def test_aec_reset_clears_previous_actions():
    inner = DummyAEC()
    env = StickyActionV1(inner, repeat_action_probability=ALWAYS)
    env.reset(seed=0)
    env.step(5)
    env.reset(seed=0)
    env.step(9)
    # The first action of the new episode has nothing to repeat.
    assert inner.received == [("agent_0", 9)]


def test_parallel_reset_clears_previous_actions():
    inner = DummyParallel()
    env = StickyActionParallelV1(inner, repeat_action_probability=ALWAYS)
    env.reset(seed=0)
    env.step({"agent_0": 5, "agent_1": 3})
    env.reset(seed=0)
    env.step({"agent_0": 9, "agent_1": 7})
    assert inner.received == [{"agent_0": 9, "agent_1": 7}]


def test_aec_reset_forwards_seed_to_the_inner_env():
    inner = DummyAEC()
    StickyActionV1(inner, repeat_action_probability=0.5).reset(seed=99)
    assert inner.seen_seed == 99


def test_parallel_reset_forwards_seed_to_the_inner_env():
    inner = DummyParallel()
    StickyActionParallelV1(inner, repeat_action_probability=0.5).reset(seed=99)
    assert inner.seen_seed == 99


def run_to_completion(env, action=4):
    """Steps every agent to death, passing None on dead steps."""
    while env.agents:
        agent = env.agent_selection
        dead = env.terminations[agent] or env.truncations[agent]
        env.step(None if dead else action)


def test_aec_dead_agents_are_stepped_with_none():
    inner = DyingAEC()
    env = StickyActionV1(inner, repeat_action_probability=ALWAYS)
    env.reset(seed=0)
    run_to_completion(env)

    # Both agents take a dead step, and the inner env must see None for it,
    # not the agent's replayed previous action.
    assert ("agent_1", None) in inner.received
    assert ("agent_0", None) in inner.received
    # None is never recorded as an action to repeat.
    assert None not in env._prev_actions.values()
    # Dead agents are dropped, so a reused agent ID cannot inherit a stale action.
    assert env._prev_actions == {}


def test_parallel_dead_agents_are_dropped_from_the_memory():
    inner = DyingParallel()
    env = StickyActionParallelV1(inner, repeat_action_probability=ALWAYS)
    env.reset(seed=0)

    env.step({"agent_0": 5, "agent_1": 3})
    assert "agent_1" not in env._prev_actions

    env.step({"agent_0": 9})
    env.step({"agent_0": 9, "agent_1": 7})
    # agent_0 is still stuck on 5, and the returning agent_1 starts fresh
    # instead of replaying the action it died on.
    assert inner.received[-1] == {"agent_0": 5, "agent_1": 7}


def test_step_after_every_agent_is_done_does_not_raise():
    # Every PettingZoo env() factory returns an OrderEnforcingWrapper, which
    # tolerates a step after all agents are done. Wrapping must not break that.
    env = StickyActionV1(
        OrderEnforcingWrapper(DyingAEC()), repeat_action_probability=0.5
    )
    env.reset(seed=0)
    run_to_completion(env)
    assert env.agents == []
    env.step(0)


def test_step_before_reset_keeps_the_usual_error():
    env = StickyActionV1(
        OrderEnforcingWrapper(DummyAEC()), repeat_action_probability=0.5
    )
    with pytest.raises(AssertionError):
        env.step(0)


def test_reused_action_buffer_does_not_defeat_stickiness():
    inner = BoxActionParallel()
    env = StickyActionParallelV1(inner, repeat_action_probability=ALWAYS)
    env.reset(seed=0)

    buffer = np.zeros(2, dtype=np.float32)
    for step in range(3):
        buffer[:] = float(step)
        env.step({"agent_0": buffer})

    # Every step should have replayed the first action, all zeros.
    assert all(np.array_equal(a, np.zeros(2, np.float32)) for a in inner.received)


def test_env_mutating_the_action_does_not_corrupt_the_memory():
    inner = BoxActionParallel(mutate=True)
    env = StickyActionParallelV1(inner, repeat_action_probability=ALWAYS)
    env.reset(seed=0)

    for _ in range(3):
        env.step({"agent_0": np.ones(2, dtype=np.float32)})

    assert all(np.array_equal(a, np.ones(2, np.float32)) for a in inner.received)


def repeat_decisions(seed):
    """Which submitted actions got replaced, over one episode seeded with ``seed``.

    Every agent submits a distinct action on every step of the window, so a
    replaced action can never coincide with the one submitted.
    """
    inner = DummyParallel()
    env = StickyActionParallelV1(inner, repeat_action_probability=0.5)
    env.reset(seed=seed)
    submitted = []
    for step in range(30):
        actions = {"agent_0": step, "agent_1": step + 32}
        submitted.append(actions)
        env.step(actions)
    return [
        received[agent] != sent[agent]
        for received, sent in zip(inner.received, submitted)
        for agent in AGENTS
    ]


def test_same_seed_gives_the_same_repeat_decisions():
    assert repeat_decisions(12345) == repeat_decisions(12345)


def test_different_seeds_give_different_repeat_decisions():
    assert repeat_decisions(0) != repeat_decisions(1)


@pytest.mark.parametrize("seed", [0, 1, 12345])
def test_repeat_rate_is_near_the_probability(seed):
    # Guards the tests above against a wrapper that always or never repeats.
    decisions = repeat_decisions(seed)
    assert 0.3 < sum(decisions) / len(decisions) < 0.7


def test_rng_is_not_the_env_rng():
    inner = DummyParallel()
    env = StickyActionParallelV1(inner, repeat_action_probability=0.5)
    env.reset(seed=42)
    env_rng, _ = seeding.np_random(42)
    assert env._np_random.bit_generator.state != env_rng.bit_generator.state


def test_repeat_decisions_do_not_track_the_env_noise():
    inner = NoisyParallel()
    env = StickyActionParallelV1(inner, repeat_action_probability=0.5)
    env.reset(seed=7)

    submitted = list(range(24))
    for action in submitted:
        env.step({"agent_0": action})

    stuck = [got != sent for got, sent in zip(inner.received, submitted)]
    env_noise_says_stuck = [n < 0.5 for n in inner.noise]
    # Seeding the wrapper with the seed the env also gets would give both the
    # same stream, and then a step was stuck exactly when the env's own noise
    # draw on the previous step was below the probability.
    assert stuck[1:] != env_noise_says_stuck[:-1]


@pytest.mark.parametrize("probability", [-0.1, 1.0, 1.5, 2])
@pytest.mark.parametrize(
    ("wrapper", "env_class"),
    [(StickyActionV1, DummyAEC), (StickyActionParallelV1, DummyParallel)],
)
def test_out_of_range_probability_raises(wrapper, env_class, probability):
    with pytest.raises(AssertionError):
        wrapper(env_class(), repeat_action_probability=probability)


def test_rejects_parallel_env():
    with pytest.raises(AssertionError):
        StickyActionV1(DummyParallel(), repeat_action_probability=0.5)


def test_str():
    env = StickyActionV1(DummyAEC(), repeat_action_probability=0.5)
    assert str(env) == "StickyActionV1<dummy_aec>"
    parallel_env = StickyActionParallelV1(
        DummyParallel(), repeat_action_probability=0.5
    )
    assert str(parallel_env) == "StickyActionParallelV1<dummy_parallel>"


def test_aec_api():
    api_test(StickyActionV1(DummyAEC(), repeat_action_probability=0.5), num_cycles=5)


def test_aec_api_with_dying_agents():
    api_test(StickyActionV1(DyingAEC(), repeat_action_probability=0.5), num_cycles=2)


def test_parallel_api():
    parallel_api_test(
        StickyActionParallelV1(DummyParallel(), repeat_action_probability=0.5),
        num_cycles=5,
    )
