from __future__ import annotations

import functools

import numpy as np
import pytest
from gymnasium.spaces import Box, Dict, Discrete

from pettingzoo.test import api_test, parallel_api_test
from pettingzoo.utils.env import AECEnv, ParallelEnv
from pettingzoo.utils.wrappers import PadObservations, PadObservationsParallel

AGENTS = ["agent_0", "agent_1"]

# agent_0 has the larger space, agent_1 gets padded up to it.
OBS_SPACES = {
    "agent_0": Box(
        low=np.zeros((2, 3), dtype=np.float32),
        high=np.array([[1, 2, 3], [4, 5, 6]], dtype=np.float32),
        dtype=np.float32,
    ),
    "agent_1": Box(low=-1.0, high=0.5, shape=(1, 2), dtype=np.float32),
}

OBS = {
    "agent_0": np.array([[0.5, 1.5, 2.5], [3.5, 4.5, 5.5]], dtype=np.float32),
    "agent_1": np.array([[0.25, -0.75]], dtype=np.float32),
}

PADDED_OBS = {
    "agent_0": OBS["agent_0"],
    "agent_1": np.array([[0.25, -0.75, 0.0], [0.0, 0.0, 0.0]], dtype=np.float32),
}


class DummyAEC(AECEnv):
    metadata = {"render_modes": [], "name": "dummy_aec"}

    def __init__(self, obs_spaces=None, obs=None):
        super().__init__()
        self.possible_agents = list(AGENTS)
        self._obs_spaces = dict(OBS_SPACES if obs_spaces is None else obs_spaces)
        self._obs = dict(OBS if obs is None else obs)

    def observation_space(self, agent):
        return self._obs_spaces[agent]

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
        return self._obs[agent]

    def step(self, action):
        self._step_count += 1
        self._cumulative_rewards[self.agent_selection] = 0.0
        self.rewards = dict.fromkeys(self.agents, 0.0)
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

    def __init__(self, obs_spaces=None, obs=None):
        super().__init__()
        self.possible_agents = list(AGENTS)
        self._obs_spaces = dict(OBS_SPACES if obs_spaces is None else obs_spaces)
        self._obs = dict(OBS if obs is None else obs)

    def observation_space(self, agent):
        return self._obs_spaces[agent]

    @functools.cache
    def action_space(self, agent):
        return Discrete(2)

    def reset(self, seed=None, options=None):
        self.agents = list(self.possible_agents)
        self._step_count = 0
        return dict(self._obs), {a: {} for a in self.agents}

    def step(self, actions):
        self._step_count += 1
        done = self._step_count >= 8
        obs = dict(self._obs)
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


@pytest.mark.parametrize(
    "wrapper,dummy",
    [(PadObservations, DummyAEC), (PadObservationsParallel, DummyParallel)],
)
def test_every_agent_gets_the_same_padded_space(wrapper, dummy):
    env = wrapper(dummy())
    space = env.observation_space("agent_0")

    assert space is env.observation_space("agent_1")
    assert space.shape == (2, 3)
    assert space.dtype == np.float32
    # each space pads its own low with min(0, its lowest) and its own high with
    # max(1e-5, its highest) before the elementwise min and max across agents, so
    # agent_1's low of -1 spreads over the whole space and agent_0's high wins.
    assert np.array_equal(space.low, np.full((2, 3), -1.0, dtype=np.float32))
    assert np.array_equal(
        space.high, np.array([[1, 2, 3], [4, 5, 6]], dtype=np.float32)
    )


@pytest.mark.parametrize("agent", AGENTS)
def test_aec_observe_is_padded(agent):
    env = PadObservations(DummyAEC())
    env.reset(seed=0)

    obs = env.observe(agent)
    assert np.array_equal(obs, PADDED_OBS[agent])
    assert env.observation_space(agent).contains(obs)


def test_largest_agent_is_untouched():
    inner = DummyAEC()
    env = PadObservations(inner)
    env.reset(seed=0)
    assert np.array_equal(env.observe("agent_0"), inner.observe("agent_0"))


@pytest.mark.parametrize("agent", AGENTS)
def test_aec_last_is_padded(agent):
    env = PadObservations(DummyAEC())
    env.reset(seed=0)
    while env.agent_selection != agent:
        env.step(0)

    obs, _, _, _, _ = env.last()
    assert np.array_equal(obs, PADDED_OBS[agent])


@pytest.mark.parametrize("agent", AGENTS)
def test_parallel_reset_and_step_are_padded(agent):
    env = PadObservationsParallel(DummyParallel())

    obs, _ = env.reset(seed=0)
    assert np.array_equal(obs[agent], PADDED_OBS[agent])
    assert env.observation_space(agent).contains(obs[agent])

    obs, _, _, _, _ = env.step(dict.fromkeys(env.agents, 0))
    assert np.array_equal(obs[agent], PADDED_OBS[agent])


def test_padding_goes_at_the_end_of_every_axis():
    spaces = {
        "agent_0": Box(low=0.0, high=1.0, shape=(3, 3), dtype=np.float32),
        "agent_1": Box(low=0.0, high=1.0, shape=(1, 2), dtype=np.float32),
    }
    obs = {
        "agent_0": np.ones((3, 3), dtype=np.float32),
        "agent_1": np.array([[0.25, 0.75]], dtype=np.float32),
    }
    env = PadObservations(DummyAEC(spaces, obs))
    env.reset(seed=0)

    expected = np.zeros((3, 3), dtype=np.float32)
    expected[0, 0] = 0.25
    expected[0, 1] = 0.75
    assert np.array_equal(env.observe("agent_1"), expected)


def test_homogeneous_spaces_are_unchanged():
    space = Box(low=-1.0, high=1.0, shape=(2, 2), dtype=np.float32)
    spaces = dict.fromkeys(AGENTS, space)
    obs = dict.fromkeys(AGENTS, np.full((2, 2), 0.5, dtype=np.float32))
    env = PadObservations(DummyAEC(spaces, obs))
    env.reset(seed=0)

    padded = env.observation_space("agent_0")
    assert padded.shape == space.shape
    assert np.array_equal(padded.low, space.low)
    assert np.array_equal(padded.high, space.high)
    assert np.array_equal(env.observe("agent_0"), obs["agent_0"])


def test_negative_high_is_clamped_so_the_padding_fits():
    # the padded entries are zeros, which sit above every real high here, so the
    # shared high has to be raised to 1e-5 for them
    spaces = {
        "agent_0": Box(low=-5.0, high=-1.0, shape=(3,), dtype=np.float32),
        "agent_1": Box(low=-5.0, high=-1.0, shape=(1,), dtype=np.float32),
    }
    obs = {
        "agent_0": np.full((3,), -2.0, dtype=np.float32),
        "agent_1": np.array([-2.0], dtype=np.float32),
    }
    env = PadObservations(DummyAEC(spaces, obs))
    env.reset(seed=0)

    space = env.observation_space("agent_1")
    assert np.allclose(space.high, np.array([-1.0, 1e-5, 1e-5], dtype=np.float32))
    assert np.array_equal(space.low, np.full((3,), -5.0, dtype=np.float32))

    padded = env.observe("agent_1")
    assert np.array_equal(padded, np.array([-2.0, 0.0, 0.0], dtype=np.float32))
    assert space.contains(padded)


def test_negative_high_clamp_truncates_for_integer_spaces():
    # same clamp, but 1e-5 truncates to 0 on the way into an int space
    spaces = {
        "agent_0": Box(low=-10, high=-1, shape=(3,), dtype=np.int8),
        "agent_1": Box(low=-10, high=-1, shape=(1,), dtype=np.int8),
    }
    obs = {
        "agent_0": np.full((3,), -5, dtype=np.int8),
        "agent_1": np.array([-5], dtype=np.int8),
    }
    env = PadObservations(DummyAEC(spaces, obs))
    env.reset(seed=0)

    space = env.observation_space("agent_1")
    assert np.array_equal(space.high, np.array([-1, 0, 0], dtype=np.int8))

    padded = env.observe("agent_1")
    assert np.array_equal(padded, np.array([-5, 0, 0], dtype=np.int8))
    assert space.contains(padded)


def test_integer_box_spaces_keep_their_dtype():
    spaces = {
        "agent_0": Box(low=0, high=255, shape=(2, 2), dtype=np.uint8),
        "agent_1": Box(low=0, high=255, shape=(1, 2), dtype=np.uint8),
    }
    obs = {
        "agent_0": np.full((2, 2), 7, dtype=np.uint8),
        "agent_1": np.array([[1, 2]], dtype=np.uint8),
    }
    env = PadObservations(DummyAEC(spaces, obs))
    env.reset(seed=0)

    space = env.observation_space("agent_1")
    padded = env.observe("agent_1")
    assert space.dtype == np.uint8
    assert padded.dtype == np.uint8
    assert np.array_equal(padded, np.array([[1, 2], [0, 0]], dtype=np.uint8))
    assert space.contains(padded)


def test_discrete_spaces_take_the_largest_n():
    spaces = {"agent_0": Discrete(3), "agent_1": Discrete(5)}
    obs = {"agent_0": 2, "agent_1": 4}
    env = PadObservations(DummyAEC(spaces, obs))
    env.reset(seed=0)

    assert env.observation_space("agent_0") == Discrete(5)
    assert env.observe("agent_0") == 2


@pytest.mark.parametrize(
    "wrapper,dummy",
    [(PadObservations, DummyAEC), (PadObservationsParallel, DummyParallel)],
)
def test_discrete_spaces_take_the_largest_n_parallel_too(wrapper, dummy):
    spaces = {"agent_0": Discrete(3), "agent_1": Discrete(5)}
    obs = {"agent_0": 2, "agent_1": 4}
    env = wrapper(dummy(spaces, obs))
    assert env.observation_space("agent_0") == Discrete(5)


@pytest.mark.parametrize(
    "spaces,expected",
    [
        # a start of 0 is the plain case: n grows, start stays put
        ({"agent_0": Discrete(3), "agent_1": Discrete(5)}, Discrete(5)),
        # the shared space has to reach up to agent_0's largest value of 7
        ({"agent_0": Discrete(3, start=5), "agent_1": Discrete(5)}, Discrete(8)),
        # nothing starts at 0, so neither does the shared space
        (
            {"agent_0": Discrete(3, start=5), "agent_1": Discrete(2, start=7)},
            Discrete(4, start=5),
        ),
        # a bigger n does not mean a bigger range
        ({"agent_0": Discrete(2), "agent_1": Discrete(4, start=10)}, Discrete(14)),
    ],
)
def test_discrete_start_is_covered(spaces, expected):
    env = PadObservations(DummyAEC(spaces))
    assert env.observation_space("agent_0") == expected

    for agent, space in spaces.items():
        for obs in range(int(space.start), int(space.start) + int(space.n)):
            assert expected.contains(obs), f"{agent} cannot observe {obs}"


def test_discrete_start_passes_the_api_test():
    spaces = {"agent_0": Discrete(3, start=5), "agent_1": Discrete(5)}
    obs = {"agent_0": np.int64(5), "agent_1": np.int64(4)}
    api_test(PadObservations(DummyAEC(spaces, obs)), num_cycles=5)


def test_parallel_discrete_and_none_pass_through():
    spaces = {"agent_0": Discrete(3), "agent_1": Discrete(5)}
    obs = {"agent_0": 2, "agent_1": None}
    env = PadObservationsParallel(DummyParallel(spaces, obs))

    observations, _ = env.reset(seed=0)
    assert observations["agent_0"] == 2
    assert observations["agent_1"] is None


def test_parallel_integer_box_spaces_keep_their_dtype():
    spaces = {
        "agent_0": Box(low=0, high=255, shape=(2, 2), dtype=np.uint8),
        "agent_1": Box(low=0, high=255, shape=(1, 2), dtype=np.uint8),
    }
    obs = {
        "agent_0": np.full((2, 2), 7, dtype=np.uint8),
        "agent_1": np.array([[1, 2]], dtype=np.uint8),
    }
    env = PadObservationsParallel(DummyParallel(spaces, obs))
    observations, _ = env.reset(seed=0)

    space = env.observation_space("agent_1")
    assert space.dtype == np.uint8
    assert observations["agent_1"].dtype == np.uint8
    assert np.array_equal(
        observations["agent_1"], np.array([[1, 2], [0, 0]], dtype=np.uint8)
    )
    assert space.contains(observations["agent_1"])


def test_mixing_discrete_and_box_raises():
    spaces = {
        "agent_0": Discrete(3),
        "agent_1": Box(low=0.0, high=1.0, shape=(2,), dtype=np.float32),
    }
    with pytest.raises(AssertionError, match="Box or Discrete, not a mix"):
        PadObservations(DummyAEC(spaces))
    with pytest.raises(AssertionError, match="Box or Discrete, not a mix"):
        PadObservationsParallel(DummyParallel(spaces))


def test_different_number_of_dimensions_raises():
    spaces = {
        "agent_0": Box(low=0.0, high=1.0, shape=(2, 2), dtype=np.float32),
        "agent_1": Box(low=0.0, high=1.0, shape=(2,), dtype=np.float32),
    }
    with pytest.raises(AssertionError, match="same number of dimensions"):
        PadObservations(DummyAEC(spaces))


def test_different_dtypes_raise():
    spaces = {
        "agent_0": Box(low=0.0, high=1.0, shape=(2,), dtype=np.float32),
        "agent_1": Box(low=0.0, high=1.0, shape=(2,), dtype=np.float64),
    }
    with pytest.raises(AssertionError, match="same dtype"):
        PadObservations(DummyAEC(spaces))


def test_unsupported_space_raises():
    space = Dict({"a": Box(low=0.0, high=1.0, shape=(2,), dtype=np.float32)})
    with pytest.raises(AssertionError, match="only supports Box and Discrete"):
        PadObservations(DummyAEC(dict.fromkeys(AGENTS, space)))


def test_missing_possible_agents_raises():
    class NoPossibleAgents(DummyAEC):
        def __init__(self):
            super().__init__()
            del self.possible_agents

    with pytest.raises(AssertionError, match="possible_agents"):
        PadObservations(NoPossibleAgents())


def test_observe_passes_through_none():
    class NoneObsEnv(DummyAEC):
        def observe(self, agent):
            return None

    env = PadObservations(NoneObsEnv())
    env.reset(seed=0)
    assert env.observe("agent_0") is None


def test_rejects_parallel_env():
    with pytest.raises(AssertionError, match="PadObservationsParallel"):
        PadObservations(DummyParallel())


def test_parallel_rejects_aec_env():
    with pytest.raises(AssertionError, match="use PadObservations instead"):
        PadObservationsParallel(DummyAEC())


def test_aec_api():
    api_test(PadObservations(DummyAEC()), num_cycles=5)


def test_parallel_api():
    parallel_api_test(PadObservationsParallel(DummyParallel()), num_cycles=5)
