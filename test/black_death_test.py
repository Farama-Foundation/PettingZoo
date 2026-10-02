from __future__ import annotations

import functools

import numpy as np
import pytest
from gymnasium.spaces import Box, Discrete

from pettingzoo.test import parallel_api_test
from pettingzoo.utils.env import ParallelEnv
from pettingzoo.utils.wrappers import BlackDeathParallelV4


AGENTS = ["agent_0", "agent_1", "agent_2"]


class EarlyDepartureParallel(ParallelEnv[str, np.ndarray, int]):
    metadata = {"render_modes": [], "name": "early_departure_parallel"}

    def __init__(self, final_truncates: bool = False, box_observations: bool = True):
        super().__init__()
        self.possible_agents = list(AGENTS)
        self.final_truncates = final_truncates
        self.box_observations = box_observations
        self.received_actions: dict[str, int] = {}
        self.last_seed = None
        self.last_options = None

    @functools.cache
    def observation_space(self, agent):
        if not self.box_observations:
            return Discrete(4)
        return Box(-1.0, 1.0, shape=(2,), dtype=np.float32)

    @functools.cache
    def action_space(self, agent):
        return Discrete(3)

    def _observation(self, agent: str) -> np.ndarray:
        index = self.possible_agents.index(agent)
        return np.full(2, 0.25 * (index + 1), dtype=np.float32)

    def reset(self, seed=None, options=None):
        self.agents = list(self.possible_agents)
        self.step_count = 0
        self.received_actions = {}
        self.last_seed = seed
        self.last_options = options
        return (
            {agent: self._observation(agent) for agent in self.agents},
            {agent: {"reset": True} for agent in self.agents},
        )

    def step(self, actions):
        assert set(actions) == set(self.agents)
        self.received_actions = dict(actions)

        if self.step_count == 0:
            observations = {
                agent: self._observation(agent) for agent in self.agents
            }
            rewards = {"agent_0": -1.0, "agent_1": 1.0, "agent_2": 2.0}
            terminations = {"agent_0": True, "agent_1": False, "agent_2": False}
            truncations = dict.fromkeys(self.agents, False)
            infos = {
                "agent_0": {"departed": True},
                "agent_1": {"departed": False},
                "agent_2": {"departed": False},
            }
            self.agents = ["agent_1", "agent_2"]
        else:
            observations = {
                agent: self._observation(agent) for agent in self.agents
            }
            rewards = {"agent_1": 3.0, "agent_2": 4.0}
            if self.final_truncates:
                terminations = dict.fromkeys(self.agents, False)
                truncations = dict.fromkeys(self.agents, True)
            else:
                terminations = dict.fromkeys(self.agents, True)
                truncations = dict.fromkeys(self.agents, False)
            infos = {agent: {"final": True} for agent in self.agents}
            self.agents = []

        self.step_count += 1
        return observations, rewards, terminations, truncations, infos

    def render(self):
        return None

    def close(self):
        pass


def test_early_departure_is_hidden_until_episode_end():
    env = BlackDeathParallelV4(EarlyDepartureParallel())
    env.reset()

    _, rewards, terminations, truncations, _ = env.step(dict.fromkeys(AGENTS, 0))

    assert env.agents == AGENTS
    assert rewards["agent_0"] == -1.0
    assert not any(terminations.values())
    assert not any(truncations.values())


def test_departed_agent_is_padded_and_its_action_is_ignored():
    inner = EarlyDepartureParallel()
    env = BlackDeathParallelV4(inner)
    env.reset()
    env.step(dict.fromkeys(AGENTS, 0))

    observations, rewards, terminations, truncations, infos = env.step(
        {"agent_0": 99, "agent_1": 1, "agent_2": 2}
    )

    assert inner.received_actions == {"agent_1": 1, "agent_2": 2}
    np.testing.assert_array_equal(
        observations["agent_0"], np.zeros(2, dtype=np.float32)
    )
    assert rewards["agent_0"] == 0.0
    assert infos["agent_0"] == {}
    assert terminations == dict.fromkeys(AGENTS, True)
    assert truncations == dict.fromkeys(AGENTS, False)
    assert env.agents == []


def test_mixed_termination_and_truncation_causes_are_preserved():
    env = BlackDeathParallelV4(EarlyDepartureParallel(final_truncates=True))
    env.reset()
    env.step(dict.fromkeys(AGENTS, 0))

    _, _, terminations, truncations, _ = env.step(dict.fromkeys(AGENTS, 0))

    assert terminations == {
        "agent_0": True,
        "agent_1": False,
        "agent_2": False,
    }
    assert truncations == {
        "agent_0": False,
        "agent_1": True,
        "agent_2": True,
    }


def test_reset_restores_full_agent_set_and_forwards_arguments():
    inner = EarlyDepartureParallel()
    env = BlackDeathParallelV4(inner)
    env.reset()
    env.step(dict.fromkeys(AGENTS, 0))
    env.step(dict.fromkeys(AGENTS, 0))
    assert env.agents == []

    observations, infos = env.reset(seed=123, options={"mode": "test"})

    assert env.agents == AGENTS
    assert set(observations) == set(AGENTS)
    assert set(infos) == set(AGENTS)
    assert inner.last_seed == 123
    assert inner.last_options == {"mode": "test"}


def test_non_box_observation_space_is_rejected():
    with pytest.raises(TypeError, match="Box observation spaces"):
        BlackDeathParallelV4(EarlyDepartureParallel(box_observations=False))


def test_parallel_api():
    parallel_api_test(
        BlackDeathParallelV4(EarlyDepartureParallel(final_truncates=True)),
        num_cycles=3,
    )
