from __future__ import annotations

import functools

import numpy as np
import pytest
from gymnasium.spaces import Box, Dict, Discrete

from pettingzoo.test import api_test, parallel_api_test
from pettingzoo.test.example_envs import (
    generated_agents_env_action_mask_obs_v0,
    generated_agents_env_v0,
)
from pettingzoo.utils.conversions import parallel_to_aec
from pettingzoo.utils.env import AECEnv, ParallelEnv
from pettingzoo.utils.wrappers import MaxObservationParallelV1, MaxObservationV1

AGENTS = ["agent_0", "agent_1"]
MAX_CYCLES = 6

# agent_0 counts down and agent_1 counts up, so a max over a window is easy to
# check by hand and the two agents cannot be confused for each other.
SEQUENCES = {
    "agent_0": [5.0, 4.0, 3.0, 2.0, 1.0, 0.0],
    "agent_1": [0.0, 1.0, 2.0, 3.0, 4.0, 5.0],
}

OBS_SPACE = Box(low=0.0, high=10.0, shape=(2,), dtype=np.float32)


def frame_obs(agent, frame):
    """Observation for a cycle. The second element moves the other way."""
    values = SEQUENCES[agent]
    value = values[min(frame, len(values) - 1)]
    return np.array([value, 10.0 - value], dtype=np.float32)


def expected_max(agent, frame, memory):
    """Elementwise max over the last `memory` cycles, clipped at the start of the episode."""
    frames = range(max(0, frame - memory + 1), frame + 1)
    return functools.reduce(np.maximum, [frame_obs(agent, f) for f in frames])


class DummyAEC(AECEnv):
    """Observations change once per cycle, not once per turn, like every real AEC env."""

    metadata = {"render_modes": [], "name": "dummy_aec"}

    def __init__(self):
        super().__init__()
        self.possible_agents = list(AGENTS)

    def observation_space(self, agent):
        return OBS_SPACE

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
        self.frame = 0
        self._idx = 0
        self.agent_selection = self.agents[0]

    def observe(self, agent):
        return frame_obs(agent, self.frame)

    def step(self, action):
        agent = self.agent_selection
        if self.terminations[agent] or self.truncations[agent]:
            self._was_dead_step(action)
            return
        self._cumulative_rewards[agent] = 0.0
        self.rewards = dict.fromkeys(self.agents, 0.0)
        self._idx = (self._idx + 1) % len(self.agents)
        if self._idx == 0:
            self.frame += 1
            if self.frame >= MAX_CYCLES:
                self.terminations = dict.fromkeys(self.agents, True)
        self.agent_selection = self.agents[self._idx]
        self._accumulate_rewards()

    def render(self):
        return None

    def close(self):
        pass


class DictObsAEC(DummyAEC):
    def observation_space(self, agent):
        return Dict({"observation": OBS_SPACE, "action_mask": Discrete(2)})


class DiscreteObsAEC(DummyAEC):
    def observation_space(self, agent):
        return Discrete(4)


class DummyParallel(ParallelEnv):
    metadata = {"render_modes": [], "name": "dummy_parallel"}

    def __init__(self):
        super().__init__()
        self.possible_agents = list(AGENTS)

    def observation_space(self, agent):
        return OBS_SPACE

    @functools.cache
    def action_space(self, agent):
        return Discrete(2)

    def reset(self, seed=None, options=None):
        self.agents = list(self.possible_agents)
        self.frame = 0
        obs = {a: frame_obs(a, self.frame) for a in self.agents}
        return obs, {a: {} for a in self.agents}

    def step(self, actions):
        self.frame += 1
        done = self.frame >= MAX_CYCLES
        obs = {a: frame_obs(a, self.frame) for a in self.agents}
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


class DictObsParallel(DummyParallel):
    def observation_space(self, agent):
        return Dict({"observation": OBS_SPACE, "action_mask": Discrete(2)})


class LeavingParallel(DummyParallel):
    """agent_1 drops out of the observation dict partway through the episode."""

    def step(self, actions):
        obs, rewards, terminations, truncations, infos = super().step(actions)
        if self.frame >= 3 and "agent_1" in self.agents:
            self.agents.remove("agent_1")
            for d in (obs, rewards, terminations, truncations, infos):
                d.pop("agent_1", None)
        return obs, rewards, terminations, truncations, infos


class FlickerParallel(ParallelEnv):
    """One pixel is lit on even cycles, the other on odd cycles."""

    metadata = {"render_modes": [], "name": "flicker"}

    def __init__(self):
        super().__init__()
        self.possible_agents = list(AGENTS)

    @functools.cache
    def observation_space(self, agent):
        return Box(low=0.0, high=1.0, shape=(2,), dtype=np.float32)

    @functools.cache
    def action_space(self, agent):
        return Discrete(2)

    def _obs(self):
        v = np.zeros(2, dtype=np.float32)
        v[self.frame % 2] = 1.0
        return {a: v.copy() for a in self.agents}

    def reset(self, seed=None, options=None):
        self.agents = list(self.possible_agents)
        self.frame = 0
        return self._obs(), {a: {} for a in self.agents}

    def step(self, actions):
        self.frame += 1
        done = self.frame >= MAX_CYCLES
        obs = self._obs()
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


def drive_aec(env, cycles, out_of_turn=False):
    """Play whole cycles and collect what each agent sees on its own turn."""
    seen = {a: [] for a in AGENTS}
    for _ in range(cycles):
        for agent in AGENTS:
            assert env.agent_selection == agent
            obs, _, term, trunc, _ = env.last()
            seen[agent].append(np.array(obs))
            if out_of_turn:
                # a centralized critic or an observation logger reading everyone
                for other in list(env.agents):
                    env.observe(other)
            env.step(None if (term or trunc) else 0)
    return seen


@pytest.mark.parametrize("agent", AGENTS)
def test_observation_space_is_unchanged(agent):
    assert MaxObservationV1(DummyAEC(), 3).observation_space(agent) == OBS_SPACE
    assert (
        MaxObservationParallelV1(DummyParallel(), 3).observation_space(agent)
        == OBS_SPACE
    )


@pytest.mark.parametrize("memory", [1, 2, 3, 4])
@pytest.mark.parametrize("out_of_turn", [False, True])
def test_aec_matches_hand_computed_max(memory, out_of_turn):
    env = MaxObservationV1(DummyAEC(), memory)
    env.reset(seed=0)
    seen = drive_aec(env, MAX_CYCLES, out_of_turn=out_of_turn)
    for agent in AGENTS:
        for cycle, obs in enumerate(seen[agent]):
            assert np.array_equal(obs, expected_max(agent, cycle, memory))
            assert env.observation_space(agent).contains(obs)


@pytest.mark.parametrize("memory", [1, 2, 3, 4])
@pytest.mark.parametrize("agent", AGENTS)
def test_parallel_matches_hand_computed_max(agent, memory):
    env = MaxObservationParallelV1(DummyParallel(), memory)
    obs, _ = env.reset(seed=0)
    assert np.array_equal(obs[agent], expected_max(agent, 0, memory))
    for frame in range(1, MAX_CYCLES):
        obs, _, _, _, _ = env.step(dict.fromkeys(env.agents, 0))
        assert np.array_equal(obs[agent], expected_max(agent, frame, memory))
        assert env.observation_space(agent).contains(obs[agent])


def test_decreasing_value_drops_out_of_the_window():
    # agent_0 sees 5, 4, 3, 2, 1, 0. With memory=3 the 5 holds the max for three
    # cycles and then falls out.
    env = MaxObservationV1(DummyAEC(), 3)
    env.reset(seed=0)
    seen = drive_aec(env, MAX_CYCLES)
    assert [float(o[0]) for o in seen["agent_0"]] == [5.0, 5.0, 5.0, 4.0, 3.0, 2.0]


def test_memory_of_one_is_a_no_op():
    env = MaxObservationV1(DummyAEC(), 1)
    env.reset(seed=0)
    seen = drive_aec(env, MAX_CYCLES)
    for agent in AGENTS:
        raw = [frame_obs(agent, cycle) for cycle in range(MAX_CYCLES)]
        assert all(np.array_equal(a, b) for a, b in zip(seen[agent], raw))
    # and the test is not vacuous: memory=3 is not the raw sequence
    env = MaxObservationV1(DummyAEC(), 3)
    env.reset(seed=0)
    maxed = drive_aec(env, MAX_CYCLES)
    assert not np.array_equal(maxed["agent_0"][3], frame_obs("agent_0", 3))


@pytest.mark.parametrize("out_of_turn", [False, True])
def test_flicker_is_removed(out_of_turn):
    # Both pixels should be lit once the window covers a lit and an unlit frame,
    # whether or not something reads observations out of turn.
    env = MaxObservationV1(parallel_to_aec(FlickerParallel()), 2)
    env.reset(seed=0)
    seen = drive_aec(env, MAX_CYCLES, out_of_turn=out_of_turn)
    for agent in AGENTS:
        for obs in seen[agent][1:]:
            assert np.array_equal(obs, np.ones(2, dtype=np.float32)), obs


def test_out_of_turn_observe_does_not_change_what_agents_see():
    for memory in (2, 3):
        quiet = MaxObservationV1(DummyAEC(), memory)
        quiet.reset(seed=0)
        a = drive_aec(quiet, MAX_CYCLES)

        noisy = MaxObservationV1(DummyAEC(), memory)
        noisy.reset(seed=0)
        b = drive_aec(noisy, MAX_CYCLES, out_of_turn=True)

        for agent in AGENTS:
            assert all(np.array_equal(x, y) for x, y in zip(a[agent], b[agent]))


def test_observe_is_pure():
    env = MaxObservationV1(DummyAEC(), 2)
    env.reset(seed=0)
    env.step(0)
    env.step(0)  # one full cycle
    first = np.array(env.observe("agent_0"))
    for _ in range(5):
        assert np.array_equal(env.observe("agent_0"), first)
    assert np.array_equal(first, expected_max("agent_0", 1, 2))


def test_histories_are_per_agent():
    memory = 3
    env = MaxObservationV1(DummyAEC(), memory)
    env.reset(seed=0)
    seen = drive_aec(env, MAX_CYCLES)
    for cycle in range(MAX_CYCLES):
        shared = np.maximum(
            expected_max("agent_0", cycle, memory),
            expected_max("agent_1", cycle, memory),
        )
        for agent in AGENTS:
            assert np.array_equal(
                seen[agent][cycle], expected_max(agent, cycle, memory)
            )
            # what the agent would see if the two histories bled together
            assert not np.array_equal(seen[agent][cycle], shared)


def test_reset_clears_history():
    env = MaxObservationV1(DummyAEC(), 3)
    env.reset(seed=0)
    drive_aec(env, 4)
    env.reset(seed=0)
    assert np.array_equal(env.observe("agent_0"), frame_obs("agent_0", 0))


def test_parallel_reset_clears_history():
    env = MaxObservationParallelV1(DummyParallel(), 3)
    env.reset(seed=0)
    for _ in range(3):
        env.step(dict.fromkeys(env.agents, 0))
    obs, _ = env.reset(seed=0)
    assert np.array_equal(obs["agent_0"], frame_obs("agent_0", 0))


def test_last_matches_hand_computed_max():
    env = MaxObservationV1(DummyAEC(), 3)
    env.reset(seed=0)
    for _ in range(4):
        env.step(0)  # two full cycles
    obs, _, _, _, _ = env.last()
    assert env.agent_selection == "agent_0"
    assert np.array_equal(obs, expected_max("agent_0", 2, 3))
    assert np.array_equal(obs, env.observe("agent_0"))


def test_agent_without_a_turn_yet_falls_back_to_the_raw_observation():
    env = MaxObservationV1(DummyAEC(), 3)
    env.reset(seed=0)
    # only agent_0 has had a turn, so agent_1 has no history to max over
    assert np.array_equal(env.observe("agent_1"), frame_obs("agent_1", 0))


def test_returned_observation_is_not_aliased():
    env = MaxObservationV1(DummyAEC(), 2)
    env.reset(seed=0)
    obs = env.observe("agent_0")
    obs[0] = 99.0
    assert np.array_equal(env.observe("agent_0"), frame_obs("agent_0", 0))


def test_source_observation_is_not_aliased():
    class MutatingEnv(DummyAEC):
        def __init__(self):
            super().__init__()
            self.buffer = np.zeros(2, dtype=np.float32)

        def observe(self, agent):
            self.buffer[:] = frame_obs(agent, self.frame)
            return self.buffer

    env = MaxObservationV1(MutatingEnv(), 2)
    env.reset(seed=0)
    env.step(0)
    env.step(0)  # one full cycle
    assert np.array_equal(env.observe("agent_0"), np.array([5.0, 6.0], np.float32))


def test_parallel_agent_leaving_the_observation_dict():
    env = MaxObservationParallelV1(LeavingParallel(), 2)
    env.reset(seed=0)
    for frame in range(1, 5):
        obs, _, _, _, _ = env.step(dict.fromkeys(env.agents, 0))
        assert np.array_equal(obs["agent_0"], expected_max("agent_0", frame, 2))
        if frame >= 3:
            assert "agent_1" not in obs


def test_rejects_dict_observations():
    with pytest.raises(ValueError, match="Dict"):
        MaxObservationV1(DictObsAEC(), 2)
    with pytest.raises(ValueError, match="Dict"):
        MaxObservationParallelV1(DictObsParallel(), 2)


def test_rejects_discrete_observations():
    with pytest.raises(ValueError, match="Discrete"):
        MaxObservationV1(DiscreteObsAEC(), 2)


def test_rejects_dict_observations_from_generated_agents():
    # This env has no possible_agents, so the check has to happen at reset.
    env = MaxObservationV1(generated_agents_env_action_mask_obs_v0.env(), 3)
    with pytest.raises(ValueError, match="Dict"):
        env.reset(seed=0)


@pytest.mark.parametrize("memory", [0, -1, 1.5, "2", None, True])
def test_rejects_bad_memory(memory):
    with pytest.raises((TypeError, ValueError)):
        MaxObservationV1(DummyAEC(), memory)
    with pytest.raises((TypeError, ValueError)):
        MaxObservationParallelV1(DummyParallel(), memory)


def test_rejects_mismatched_env_type():
    with pytest.raises(AssertionError):
        MaxObservationV1(DummyParallel(), 2)
    with pytest.raises(AssertionError):
        MaxObservationParallelV1(DummyAEC(), 2)


def test_str():
    assert str(MaxObservationV1(DummyAEC(), 2)).startswith("MaxObservationV1<")
    assert str(MaxObservationParallelV1(DummyParallel(), 2)).startswith(
        "MaxObservationParallelV1<"
    )


def test_aec_api():
    api_test(MaxObservationV1(DummyAEC(), 2), num_cycles=10)


def test_aec_api_on_converted_parallel_env():
    api_test(MaxObservationV1(parallel_to_aec(FlickerParallel()), 2), num_cycles=10)


def test_aec_api_with_generated_agents():
    # agents come and go mid-episode, which exercises the no-history-yet path
    api_test(MaxObservationV1(generated_agents_env_v0.env(), 2), num_cycles=20)


def test_parallel_api():
    parallel_api_test(MaxObservationParallelV1(DummyParallel(), 2), num_cycles=10)
