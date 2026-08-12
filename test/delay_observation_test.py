from __future__ import annotations

from typing import Any

import gymnasium
import numpy as np
import pytest
from typing_extensions import override

from pettingzoo.test import api_test, parallel_api_test
from pettingzoo.test.example_envs import (
    generated_agents_env_v0,
    generated_agents_parallel_v0,
)
from pettingzoo.utils.agent_selector import AgentSelector
from pettingzoo.utils.env import AECEnv, ParallelEnv
from pettingzoo.utils.wrappers import DelayObservation, DelayObservationParallel

AGENTS = ["agent_0", "agent_1"]


class DeterministicAECEnv(AECEnv[str, Any, int]):
    metadata = {"name": "deterministic_delay_aec_v0"}

    def __init__(self, masked: bool = False):
        super().__init__()
        self.possible_agents = AGENTS[:]
        self.masked = masked
        self._observation_spaces = {
            agent: self._make_observation_space() for agent in self.possible_agents
        }
        self._action_spaces = {
            agent: gymnasium.spaces.Discrete(3) for agent in self.possible_agents
        }

    def _make_observation_space(self):
        if self.masked:
            return gymnasium.spaces.Dict(
                {
                    "observation": gymnasium.spaces.Box(
                        low=0, high=100, shape=(1,), dtype=np.int64
                    ),
                    "action_mask": gymnasium.spaces.MultiBinary(3),
                }
            )
        return gymnasium.spaces.Box(low=0, high=100, shape=(1,), dtype=np.int64)

    @override
    def observation_space(self, agent: str):
        return self._observation_spaces[agent]

    @override
    def action_space(self, agent: str):
        return self._action_spaces[agent]

    @override
    def reset(
        self, seed: int | None = None, options: dict[str, Any] | None = None
    ) -> None:
        self.agents = self.possible_agents[:]
        self.rewards = dict.fromkeys(self.agents, 0.0)
        self._cumulative_rewards = dict.fromkeys(self.agents, 0.0)
        self.terminations = dict.fromkeys(self.agents, False)
        self.truncations = dict.fromkeys(self.agents, False)
        self.infos = {agent: {} for agent in self.agents}
        self._observation_updates = dict.fromkeys(self.agents, 0)
        self._agent_selector = AgentSelector(self.agents)
        self.agent_selection = self._agent_selector.reset()

    @override
    def observe(self, agent: str):
        value = 10 * (self.possible_agents.index(agent) + 1)
        value += self._observation_updates[agent]
        observation = np.array([value], dtype=np.int64)
        if self.masked:
            return {
                "observation": observation,
                "action_mask": np.array([1, 0, 1], dtype=np.int8),
            }
        return observation

    @override
    def step(self, action: int) -> None:
        self._cumulative_rewards[self.agent_selection] = 0
        self._clear_rewards()
        self.agent_selection = self._agent_selector.next()
        self._observation_updates[self.agent_selection] += 1
        self._accumulate_rewards()

    @override
    def state(self) -> np.ndarray:
        return np.array(
            [self._observation_updates[agent] for agent in self.possible_agents],
            dtype=np.int64,
        )

    @override
    def render(self) -> None:
        return None


class DeterministicParallelEnv(ParallelEnv[str, Any, int]):
    metadata = {"name": "deterministic_delay_parallel_v0"}

    def __init__(self, masked: bool = False):
        super().__init__()
        self.possible_agents = AGENTS[:]
        self.masked = masked
        self._observation_spaces = {
            agent: self._make_observation_space() for agent in self.possible_agents
        }
        self._action_spaces = {
            agent: gymnasium.spaces.Discrete(3) for agent in self.possible_agents
        }

    def _make_observation_space(self):
        if self.masked:
            return gymnasium.spaces.Dict(
                {
                    "observation": gymnasium.spaces.Box(
                        low=0, high=100, shape=(1,), dtype=np.int64
                    ),
                    "action_mask": gymnasium.spaces.MultiBinary(3),
                }
            )
        return gymnasium.spaces.Box(low=0, high=100, shape=(1,), dtype=np.int64)

    @override
    def observation_space(self, agent: str):
        return self._observation_spaces[agent]

    @override
    def action_space(self, agent: str):
        return self._action_spaces[agent]

    def _observe(self, agent: str):
        value = 10 * (self.possible_agents.index(agent) + 1) + self._step_count
        observation = np.array([value], dtype=np.int64)
        if self.masked:
            return {
                "observation": observation,
                "action_mask": np.array([1, 0, 1], dtype=np.int8),
            }
        return observation

    @override
    def reset(self, seed: int | None = None, options: dict[str, Any] | None = None):
        self.agents = self.possible_agents[:]
        self._step_count = 0
        observations = {agent: self._observe(agent) for agent in self.agents}
        infos = {agent: {"reset": True} for agent in self.agents}
        return observations, infos

    @override
    def step(self, actions: dict[str, int]):
        self._step_count += 1
        observations = {agent: self._observe(agent) for agent in self.agents}
        rewards = {agent: float(i) for i, agent in enumerate(self.agents)}
        terminations = dict.fromkeys(self.agents, False)
        truncations = dict.fromkeys(self.agents, False)
        infos = {agent: {"step": self._step_count} for agent in self.agents}
        return observations, rewards, terminations, truncations, infos

    @override
    def state(self) -> np.ndarray:
        return np.array([self._step_count], dtype=np.int64)

    @override
    def render(self) -> None:
        return None


@pytest.mark.parametrize("wrapper", [DelayObservation, DelayObservationParallel])
def test_delay_validation(wrapper) -> None:
    env = (
        DeterministicAECEnv()
        if wrapper is DelayObservation
        else DeterministicParallelEnv()
    )

    assert wrapper(env, delay=np.int64(3)).delay == 3
    with pytest.raises(TypeError, match="delay is expected to be an integer"):
        wrapper(env, delay=1.5)
    with pytest.raises(TypeError, match="delay is expected to be an integer"):
        wrapper(env, delay=True)
    with pytest.raises(ValueError, match="greater than or equal to zero"):
        wrapper(env, delay=-1)


@pytest.mark.parametrize(
    ("delay", "expected"),
    [
        (0, {"agent_0": [10, 11, 12, 13], "agent_1": [21, 22, 23, 24]}),
        (1, {"agent_0": [0, 10, 11, 12], "agent_1": [0, 21, 22, 23]}),
        (2, {"agent_0": [0, 0, 10, 11], "agent_1": [0, 0, 21, 22]}),
    ],
)
def test_aec_delay_timeline_and_observe_idempotency(delay, expected) -> None:
    env = DelayObservation(DeterministicAECEnv(), delay=delay)
    env.reset()
    observations = {agent: [] for agent in AGENTS}

    for _ in range(8):
        agent = env.agent_selection
        observation = env.observe(agent)
        assert observation is not None
        observations[agent].append(int(observation[0]))
        assert env.observation_space(agent).contains(observation)

        for _ in range(20):
            np.testing.assert_array_equal(env.observe(agent), observation)
        env.step(0)

    assert observations == expected


@pytest.mark.parametrize("delay", [0, 1, 2])
def test_parallel_delay_timeline(delay) -> None:
    env = DelayObservationParallel(DeterministicParallelEnv(), delay=delay)
    observations, reset_infos = env.reset()
    timeline = {agent: [int(observations[agent][0])] for agent in env.possible_agents}
    assert reset_infos == {agent: {"reset": True} for agent in AGENTS}

    for _ in range(3):
        observations, rewards, terminations, truncations, infos = env.step(
            dict.fromkeys(env.agents, 0)
        )
        for agent in env.possible_agents:
            timeline[agent].append(int(observations[agent][0]))
            assert env.observation_space(agent).contains(observations[agent])
        assert rewards == {"agent_0": 0.0, "agent_1": 1.0}
        assert not any(terminations.values())
        assert not any(truncations.values())
        assert infos == {agent: {"step": env.unwrapped._step_count} for agent in AGENTS}

    raw = {"agent_0": [10, 11, 12, 13], "agent_1": [20, 21, 22, 23]}
    expected = {
        agent: [0] * delay + values[: 4 - delay] for agent, values in raw.items()
    }
    assert timeline == expected


def test_aec_reset_clears_delay_history() -> None:
    env = DelayObservation(DeterministicAECEnv(), delay=1)
    env.reset()
    env.step(0)
    env.step(0)
    np.testing.assert_array_equal(env.observe("agent_0"), [10])

    env.reset()
    np.testing.assert_array_equal(env.observe("agent_0"), [0])


def test_parallel_reset_clears_delay_history() -> None:
    env = DelayObservationParallel(DeterministicParallelEnv(), delay=1)
    env.reset()
    observations, *_ = env.step(dict.fromkeys(env.agents, 0))
    np.testing.assert_array_equal(observations["agent_0"], [10])

    observations, _ = env.reset()
    np.testing.assert_array_equal(observations["agent_0"], [0])


def test_aec_unselected_agent_observation_does_not_start_history() -> None:
    env = DelayObservation(DeterministicAECEnv(), delay=1)
    env.reset()

    for _ in range(20):
        np.testing.assert_array_equal(env.observe("agent_1"), [0])

    env.step(0)
    np.testing.assert_array_equal(env.observe("agent_1"), [0])
    env.step(0)
    env.step(0)
    np.testing.assert_array_equal(env.observe("agent_1"), [21])


def test_initial_observation_is_valid_when_box_excludes_zero() -> None:
    base_env = DeterministicAECEnv()
    base_env._observation_spaces = {
        agent: gymnasium.spaces.Box(low=5, high=100, shape=(1,), dtype=np.int64)
        for agent in base_env.possible_agents
    }
    env = DelayObservation(base_env, delay=1)
    env.reset()

    observation = env.observe("agent_0")
    np.testing.assert_array_equal(observation, [5])
    assert env.observation_space("agent_0").contains(observation)


def test_aec_step_handles_episode_end_without_selected_agent() -> None:
    base_env = DeterministicAECEnv()
    env = DelayObservation(base_env, delay=1)
    env.reset()

    def terminate(_: int) -> None:
        base_env.agents = []

    base_env.step = terminate
    env.step(0)
    assert env.agents == []


@pytest.mark.parametrize(
    "wrapper,env",
    [
        (DelayObservation, DeterministicAECEnv(masked=True)),
        (DelayObservationParallel, DeterministicParallelEnv(masked=True)),
    ],
)
def test_action_mask_placeholder_is_all_ones(wrapper, env) -> None:
    wrapped_env = wrapper(env, delay=1)
    if isinstance(wrapped_env, DelayObservation):
        wrapped_env.reset()
        observation = wrapped_env.observe(wrapped_env.agent_selection)
    else:
        observations, _ = wrapped_env.reset()
        observation = observations["agent_0"]

    assert observation is not None
    np.testing.assert_array_equal(observation["observation"], [0])
    np.testing.assert_array_equal(observation["action_mask"], [1, 1, 1])
    assert wrapped_env.observation_space("agent_0").contains(observation)


def test_aec_action_mask_is_delayed_with_observation() -> None:
    env = DelayObservation(DeterministicAECEnv(masked=True), delay=1)
    env.reset()
    env.step(0)
    env.step(0)
    observation = env.observe("agent_0")

    assert observation is not None
    np.testing.assert_array_equal(observation["observation"], [10])
    np.testing.assert_array_equal(observation["action_mask"], [1, 0, 1])


def test_parallel_action_mask_is_delayed_with_observation() -> None:
    env = DelayObservationParallel(DeterministicParallelEnv(masked=True), delay=1)
    env.reset()
    observations, *_ = env.step(dict.fromkeys(env.agents, 0))

    np.testing.assert_array_equal(observations["agent_0"]["observation"], [10])
    np.testing.assert_array_equal(observations["agent_0"]["action_mask"], [1, 0, 1])


def test_aec_api() -> None:
    api_test(DelayObservation(generated_agents_env_v0.raw_env(max_cycles=5), delay=2))


def test_parallel_api() -> None:
    parallel_api_test(
        DelayObservationParallel(
            generated_agents_parallel_v0.parallel_env(max_cycles=5), delay=2
        ),
        num_cycles=10,
    )
