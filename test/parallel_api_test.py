from __future__ import annotations

import warnings

import numpy as np
import pytest
from gymnasium.spaces import Box, Dict, Discrete, MultiBinary, MultiDiscrete

from pettingzoo.test import parallel_api_test
from pettingzoo.utils.env import ParallelEnv


class ObservationEnv(ParallelEnv):
    metadata = {"render_modes": [], "name": "observation_test"}

    def __init__(
        self, observation_space, observation_override=None, override_phase=None
    ):
        self.possible_agents = ["agent_0"]
        self._observation_space = observation_space
        self._action_space = Discrete(2)
        self.observation_override = observation_override
        self.override_phase = override_phase
        self.step_calls = 0

    def observation_space(self, agent):
        return self._observation_space

    def action_space(self, agent):
        return self._action_space

    def _observations(self, phase):
        observation = (
            self.observation_override
            if phase == self.override_phase
            else self._observation_space.sample()
        )
        return {"agent_0": observation}

    def reset(self, seed=None, options=None):
        self.agents = self.possible_agents[:]
        return self._observations("reset"), {"agent_0": {}}

    def step(self, actions):
        self.step_calls += 1
        return (
            self._observations("step"),
            {"agent_0": 0},
            {"agent_0": False},
            {"agent_0": False},
            {"agent_0": {}},
        )


MASKED_SPACE = Dict(
    {
        "observation": Box(0, 1, shape=(2,), dtype=np.float32),
        "action_mask": MultiBinary(2),
    }
)


@pytest.mark.parametrize("phase", ["reset", "step"])
@pytest.mark.parametrize(
    "space, observation",
    [
        (Box(0, 1, shape=(2,), dtype=np.float32), np.zeros(3, dtype=np.float32)),
        (Box(0, 1, shape=(2,), dtype=np.float32), np.zeros(2, dtype=np.float64)),
        (Box(0, 1, shape=(2,), dtype=np.float32), np.array([0, 2], dtype=np.float32)),
        (MASKED_SPACE, {"observation": np.zeros(2, dtype=np.float32)}),
        (MultiDiscrete([2, 3]), np.array([0, 3])),
        (
            MultiDiscrete([2, 3]),
            {
                "observation": np.array([0, 1]),
                "action_mask": np.ones(2, dtype=np.int8),
            },
        ),
    ],
    ids=["shape", "dtype", "bounds", "missing-mask", "multidiscrete", "dict-mismatch"],
)
def test_invalid_observation_fails(space, observation, phase):
    env = ObservationEnv(space, observation, phase)

    with pytest.raises(AssertionError) as exc_info:
        parallel_api_test(env, num_cycles=2)

    assert "agent_0" in str(exc_info.value)
    assert phase in str(exc_info.value)
    assert env.step_calls == (0 if phase == "reset" else 1)


def test_valid_dict_observations_with_action_mask():
    parallel_api_test(ObservationEnv(MASKED_SPACE), num_cycles=2)


def test_invalid_observation_from_seeded_reset_fails():
    class SeededResetObservationEnv(ObservationEnv):
        def reset(self, seed=None, options=None):
            observations, infos = super().reset(seed=seed, options=options)
            if seed == 0:
                observations["agent_0"] = np.full(2, 2, dtype=np.float32)
            return observations, infos

    env = SeededResetObservationEnv(Box(0, 1, shape=(2,), dtype=np.float32))
    with pytest.raises(AssertionError, match=r"agent_0.*reset"):
        parallel_api_test(env, num_cycles=2)

    assert env.step_calls == 0


@pytest.mark.parametrize("phase", ["reset", "step"])
def test_valid_observation_with_castable_dtype(phase):
    env = ObservationEnv(
        Box(0, 1, shape=(2,), dtype=np.float64),
        np.zeros(2, dtype=np.float32),
        phase,
    )
    parallel_api_test(env, num_cycles=2)


def test_missing_step_observation_keeps_existing_warning():
    class MissingObservationEnv(ObservationEnv):
        def step(self, actions):
            _, rewards, terminations, truncations, infos = super().step(actions)
            return {}, rewards, terminations, truncations, infos

    env = MissingObservationEnv(Box(0, 1, shape=(2,), dtype=np.float32))
    with pytest.warns(UserWarning, match="Live agent was not given observation"):
        parallel_api_test(env, num_cycles=1)


class ChangingAgentsEnv(ParallelEnv):
    metadata = {"render_modes": [], "name": "changing_agents_observation_test"}

    def __init__(self, possible_agents=True, invalid_joining_agent=False):
        if possible_agents:
            self.possible_agents = [0, 1]
        self._observation_spaces = {
            0: Box(0, 1, shape=(2,), dtype=np.float32),
            1: Discrete(3),
        }
        self._action_space = Discrete(2)
        self.invalid_joining_agent = invalid_joining_agent

    def observation_space(self, agent):
        # Detect attempts to check observations for agents that have left.
        assert agent in self.agents
        return self._observation_spaces[agent]

    def action_space(self, agent):
        return self._action_space

    def reset(self, seed=None, options=None):
        self.agents = [0]
        self.steps = 0
        return (
            {0: np.zeros(2, dtype=np.float32), "common": None},
            {0: {}, "common": {}},
        )

    def step(self, actions):
        self.steps += 1
        if self.steps == 1:
            self.agents = [0, 1]
            observations = {
                0: np.zeros(2, dtype=np.float32),
                1: 3 if self.invalid_joining_agent else 2,
            }
            terminations = {0: False, 1: False}
        elif self.steps == 2:
            self.agents = [1]
            observations = {0: None, 1: 2}
            terminations = {0: True, 1: False}
        else:
            self.agents = []
            observations = {1: None}
            terminations = {1: True}
        return (
            observations,
            dict.fromkeys(observations, 0),
            terminations,
            dict.fromkeys(observations, False),
            {agent: {} for agent in observations},
        )


@pytest.mark.parametrize("possible_agents", [True, False])
def test_valid_observations_with_changing_agents(possible_agents):
    env = ChangingAgentsEnv(possible_agents=possible_agents)

    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter("always")
        parallel_api_test(env, num_cycles=3)

    assert env.agents == []
    assert all(
        "possible_agents" in str(w.message) or "No agents present" in str(w.message)
        for w in caught
    )


def test_invalid_observation_from_joining_agent_fails():
    env = ChangingAgentsEnv(invalid_joining_agent=True)

    with pytest.raises(AssertionError) as exc_info:
        parallel_api_test(env, num_cycles=3)

    assert "1" in str(exc_info.value)
    assert "step" in str(exc_info.value)
    assert env.steps == 1
