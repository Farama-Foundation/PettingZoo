from __future__ import annotations

import functools
import pickle

import numpy as np
import pytest
from gymnasium.spaces import Box, Dict, Discrete, MultiDiscrete

from pettingzoo.test import api_test, parallel_api_test
from pettingzoo.test.example_envs import (
    generated_agents_env_action_mask_obs_v0,
    generated_agents_env_v0,
)
from pettingzoo.utils.conversions import parallel_to_aec
from pettingzoo.utils.env import AECEnv, ParallelEnv
from pettingzoo.utils.wrappers import FrameStackV3

AGENTS = ["agent_0", "agent_1"]
MAX_CYCLES = 6
INITIALS = ["first_obs", "zeros"]
STACK_DIMS = [-1, 0]

# (frame shape for stack_dim=-1, frame shape for stack_dim=0). 3D frames are
# channel-last for -1 and channel-first for 0, as they would be in practice.
SHAPES = {
    "1d": {-1: (3,), 0: (3,)},
    "2d": {-1: (2, 3), 0: (2, 3)},
    "3d": {-1: (2, 3, 2), 0: (2, 2, 3)},
}


def stacked_shape(shape, stack_dim, k):
    """The stacked shape, written out by hand rather than computed like the wrapper does."""
    if len(shape) == 1:
        return (shape[0] * k,)
    if len(shape) == 2:
        return shape + (k,) if stack_dim == -1 else (k,) + shape
    if stack_dim == -1:
        return shape[:2] + (shape[2] * k,)
    return (shape[0] * k,) + shape[1:]


def slot(stack, shape, stack_dim, i):
    """Frame i (0 is the oldest) out of a stacked observation."""
    if len(shape) == 1:
        n = shape[0]
        return stack[i * n : (i + 1) * n]
    if len(shape) == 2:
        return stack[:, :, i] if stack_dim == -1 else stack[i]
    if stack_dim == -1:
        c = shape[2]
        return stack[:, :, i * c : (i + 1) * c]
    c = shape[0]
    return stack[i * c : (i + 1) * c]


def frame_obs(agent, frame, shape, dtype=np.float32):
    """Every element, frame and agent is different, and nothing is ever zero."""
    offset = 1 + 20 * frame + 10 * AGENTS.index(agent)
    return (np.arange(np.prod(shape)).reshape(shape) + offset).astype(dtype)


def expected_frames(agent, frame, shape, k, initial, dtype=np.float32):
    """The k frames, oldest first, an agent should see at a frame."""
    frames = []
    for f in range(frame - k + 1, frame + 1):
        if f >= 0:
            frames.append(frame_obs(agent, f, shape, dtype))
        elif initial == "zeros":
            frames.append(np.zeros(shape, dtype=dtype))
        else:
            frames.append(frame_obs(agent, 0, shape, dtype))
    return frames


def assert_stack(stack, agent, frame, shape, stack_dim, k, initial):
    assert stack.shape == stacked_shape(shape, stack_dim, k)
    for i, want in enumerate(expected_frames(agent, frame, shape, k, initial)):
        assert np.array_equal(slot(stack, shape, stack_dim, i), want), (i, frame)


class DummyAEC(AECEnv):
    """Observations change once per cycle, not once per turn, like every real AEC env."""

    metadata = {"render_modes": [], "name": "dummy_aec"}

    def __init__(self, shape=(3,), dtype=np.float32):
        super().__init__()
        self.possible_agents = list(AGENTS)
        self.shape = shape
        self.dtype = dtype

    @functools.cache
    def observation_space(self, agent):
        return Box(low=0, high=255, shape=self.shape, dtype=self.dtype)

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
        return frame_obs(agent, self.frame, self.shape, self.dtype)

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


class DiscreteAEC(DummyAEC):
    """Agent i sees (frame + i) % 3, offset by the space's start."""

    def __init__(self, start=0):
        super().__init__()
        self.start = start

    @functools.cache
    def observation_space(self, agent):
        return Discrete(3, start=self.start)

    def observe(self, agent):
        return np.int64(self.start + (self.frame + AGENTS.index(agent)) % 3)


class PositiveLowAEC(DummyAEC):
    """A Box that does not contain 0, so zero-filled frames would fall outside it."""

    @functools.cache
    def observation_space(self, agent):
        return Box(low=1, high=255, shape=self.shape, dtype=self.dtype)


class DictObsAEC(DummyAEC):
    def observation_space(self, agent):
        return Dict({"observation": Box(0, 1, (3,)), "action_mask": Discrete(2)})


class DummyParallel(ParallelEnv):
    metadata = {"render_modes": [], "name": "dummy_parallel"}

    def __init__(self, shape=(3,), dtype=np.float32):
        super().__init__()
        self.possible_agents = list(AGENTS)
        self.shape = shape
        self.dtype = dtype

    @functools.cache
    def observation_space(self, agent):
        return Box(low=0, high=255, shape=self.shape, dtype=self.dtype)

    @functools.cache
    def action_space(self, agent):
        return Discrete(2)

    def _obs(self):
        return {
            a: frame_obs(a, self.frame, self.shape, self.dtype) for a in self.agents
        }

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


class DictObsParallel(DummyParallel):
    def observation_space(self, agent):
        return Dict({"observation": Box(0, 1, (3,)), "action_mask": Discrete(2)})


class RejoinParallel(DummyParallel):
    """agent_1 is gone for frames 2 and 3, and back from frame 4."""

    def _obs(self):
        if 2 <= self.frame <= 3:
            self.agents = ["agent_0"]
        else:
            self.agents = list(self.possible_agents)
        return super()._obs()

    def step(self, actions):
        self.frame += 1
        obs = self._obs()
        done = self.frame >= MAX_CYCLES
        rewards = dict.fromkeys(self.agents, 0.0)
        terminations = dict.fromkeys(self.agents, done)
        truncations = dict.fromkeys(self.agents, False)
        infos = {a: {} for a in self.agents}
        if done:
            self.agents = []
        return obs, rewards, terminations, truncations, infos


class LeavingParallel(DummyParallel):
    """agent_1 terminates at frame 2 and is gone after that, as the API expects."""

    def step(self, actions):
        obs, rewards, terminations, truncations, infos = super().step(actions)
        if self.frame == 2 and "agent_1" in obs:
            terminations["agent_1"] = True
            self.agents = [a for a in self.agents if a != "agent_1"]
        return obs, rewards, terminations, truncations, infos

    def _obs(self):
        if self.frame > 2:
            self.agents = [a for a in self.agents if a != "agent_1"]
        return super()._obs()


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


@pytest.mark.parametrize("dtype", [np.float32, np.uint8, np.int64])
@pytest.mark.parametrize("stack_dim", STACK_DIMS)
@pytest.mark.parametrize("dims", SHAPES)
@pytest.mark.parametrize("initial", INITIALS)
def test_box_space_shape_and_dtype(initial, dims, stack_dim, dtype):
    shape = SHAPES[dims][stack_dim]
    for env in (
        FrameStackV3(DummyAEC(shape, dtype), 3, stack_dim, initial),
        FrameStackV3(DummyParallel(shape, dtype), 3, stack_dim, initial),
    ):
        space = env.observation_space("agent_0")
        assert isinstance(space, Box)
        assert space.shape == stacked_shape(shape, stack_dim, 3)
        assert space.dtype == dtype
        assert np.all(space.low == 0) and np.all(space.high == 255)
        # the same object every time, so seeding the space works
        assert env.observation_space("agent_0") is space


@pytest.mark.parametrize("stack_size", [1, 2, 3, 7])
@pytest.mark.parametrize("stack_dim", STACK_DIMS)
@pytest.mark.parametrize("dims", SHAPES)
@pytest.mark.parametrize("initial", INITIALS)
def test_aec_matches_hand_computed_stack(initial, dims, stack_dim, stack_size):
    shape = SHAPES[dims][stack_dim]
    env = FrameStackV3(DummyAEC(shape), stack_size, stack_dim, initial)
    env.reset(seed=0)
    seen = drive_aec(env, MAX_CYCLES)
    for agent in AGENTS:
        for cycle, obs in enumerate(seen[agent]):
            assert_stack(obs, agent, cycle, shape, stack_dim, stack_size, initial)
            assert obs.dtype == np.float32
            assert env.observation_space(agent).contains(obs)


@pytest.mark.parametrize("stack_size", [1, 2, 3, 7])
@pytest.mark.parametrize("stack_dim", STACK_DIMS)
@pytest.mark.parametrize("dims", SHAPES)
@pytest.mark.parametrize("initial", INITIALS)
def test_parallel_matches_hand_computed_stack(initial, dims, stack_dim, stack_size):
    shape = SHAPES[dims][stack_dim]
    env = FrameStackV3(DummyParallel(shape), stack_size, stack_dim, initial)
    obs, _ = env.reset(seed=0)
    for frame in range(MAX_CYCLES):
        if frame > 0:
            obs, _, _, _, _ = env.step(dict.fromkeys(env.agents, 0))
        for agent in AGENTS:
            assert_stack(
                obs[agent], agent, frame, shape, stack_dim, stack_size, initial
            )
            assert env.observation_space(agent).contains(obs[agent])


def test_initial_modes_differ_only_before_the_history_is_full():
    k = 3
    first = FrameStackV3(DummyAEC(), k, initial="first_obs")
    zeros = FrameStackV3(DummyAEC(), k, initial="zeros")
    first.reset(seed=0)
    zeros.reset(seed=0)
    a = drive_aec(first, MAX_CYCLES)
    b = drive_aec(zeros, MAX_CYCLES)
    for cycle in range(MAX_CYCLES):
        same = np.array_equal(a["agent_0"][cycle], b["agent_0"][cycle])
        assert same == (cycle >= k - 1), cycle
    # v1: zeros in front of the first frame. v2: the first frame repeated.
    assert np.array_equal(b["agent_0"][0][:6], np.zeros(6))
    assert np.array_equal(a["agent_0"][0], np.tile(frame_obs("agent_0", 0, (3,)), k))


def test_default_is_first_obs_with_four_frames_on_the_last_axis():
    env = FrameStackV3(DummyAEC((2, 3)))
    assert (env.stack_size, env.stack_dim, env.initial) == (4, -1, "first_obs")
    assert env.observation_space("agent_0").shape == (2, 3, 4)


@pytest.mark.parametrize("start", [0, 5])
@pytest.mark.parametrize("initial", INITIALS)
def test_discrete_encoding(initial, start):
    k = 3
    env = FrameStackV3(DiscreteAEC(start), k, initial=initial)
    assert env.observation_space("agent_0") == Discrete(3**k)
    env.reset(seed=0)
    seen = drive_aec(env, MAX_CYCLES)
    for agent in AGENTS:
        i = AGENTS.index(agent)
        for cycle, obs in enumerate(seen[agent]):
            digits = []
            for f in range(cycle - k + 1, cycle + 1):
                if f >= 0:
                    digits.append((f + i) % 3)
                else:
                    digits.append(0 if initial == "zeros" else i % 3)
            # the oldest frame is the most significant digit
            want = digits[0] * 9 + digits[1] * 3 + digits[2]
            assert int(obs) == want, (agent, cycle)
            assert env.observation_space(agent).contains(obs)


def test_discrete_space_that_does_not_fit_in_int64_is_rejected():
    with pytest.raises(ValueError, match="int64"):
        FrameStackV3(DiscreteAEC(), 64)


def test_zeros_mode_widens_bounds_to_include_zero():
    zeros = FrameStackV3(PositiveLowAEC(), 3, initial="zeros")
    first = FrameStackV3(PositiveLowAEC(), 3, initial="first_obs")
    assert np.all(zeros.observation_space("agent_0").low == 0)
    assert np.all(first.observation_space("agent_0").low == 1)
    zeros.reset(seed=0)
    assert zeros.observation_space("agent_0").contains(zeros.observe("agent_0"))


@pytest.mark.parametrize("initial", INITIALS)
def test_out_of_turn_observe_does_not_change_what_agents_see(initial):
    quiet = FrameStackV3(DummyAEC(), 3, initial=initial)
    quiet.reset(seed=0)
    a = drive_aec(quiet, MAX_CYCLES)

    noisy = FrameStackV3(DummyAEC(), 3, initial=initial)
    noisy.reset(seed=0)
    b = drive_aec(noisy, MAX_CYCLES, out_of_turn=True)

    for agent in AGENTS:
        assert all(np.array_equal(x, y) for x, y in zip(a[agent], b[agent]))


def test_repeated_observe_returns_the_same_stack():
    env = FrameStackV3(DummyAEC(), 3)
    env.reset(seed=0)
    env.step(0)
    env.step(0)  # one full cycle
    first = env.observe("agent_0")
    for _ in range(5):
        assert np.array_equal(env.observe("agent_0"), first)
        assert np.array_equal(env.last()[0], first)
    assert_stack(first, "agent_0", 1, (3,), -1, 3, "first_obs")


def test_histories_are_per_agent():
    env = FrameStackV3(DummyAEC(), 3)
    env.reset(seed=0)
    seen = drive_aec(env, MAX_CYCLES)
    for cycle in range(MAX_CYCLES):
        assert not np.array_equal(seen["agent_0"][cycle], seen["agent_1"][cycle])
        for agent in AGENTS:
            assert_stack(seen[agent][cycle], agent, cycle, (3,), -1, 3, "first_obs")


@pytest.mark.parametrize("initial", INITIALS)
def test_reset_clears_history(initial):
    env = FrameStackV3(DummyAEC(), 3, initial=initial)
    env.reset(seed=0)
    drive_aec(env, 4)
    env.reset(seed=0)
    assert_stack(env.observe("agent_0"), "agent_0", 0, (3,), -1, 3, initial)


@pytest.mark.parametrize("initial", INITIALS)
def test_parallel_reset_clears_history(initial):
    env = FrameStackV3(DummyParallel(), 3, initial=initial)
    env.reset(seed=0)
    for _ in range(3):
        env.step(dict.fromkeys(env.agents, 0))
    obs, _ = env.reset(seed=0)
    for agent in AGENTS:
        assert_stack(obs[agent], agent, 0, (3,), -1, 3, initial)


@pytest.mark.parametrize("initial", INITIALS)
def test_agent_without_a_turn_yet_sees_the_stack_its_first_turn_starts(initial):
    env = FrameStackV3(DummyAEC(), 3, initial=initial)
    env.reset(seed=0)
    # only agent_0 has had a turn
    before = env.observe("agent_1")
    assert_stack(before, "agent_1", 0, (3,), -1, 3, initial)
    env.step(0)
    assert env.agent_selection == "agent_1"
    assert np.array_equal(env.observe("agent_1"), before)


@pytest.mark.parametrize("initial", INITIALS)
def test_parallel_agent_leaving_and_coming_back_starts_fresh(initial):
    env = FrameStackV3(RejoinParallel(), 3, initial=initial)
    obs, _ = env.reset(seed=0)
    for frame in range(1, MAX_CYCLES):
        obs, _, _, _, _ = env.step(dict.fromkeys(env.agents, 0))
        assert_stack(obs["agent_0"], "agent_0", frame, (3,), -1, 3, initial)
        if 2 <= frame <= 3:
            assert "agent_1" not in obs
    # agent_1 came back at frame 4, so frame 5 is the second frame of its new
    # history. Frames 0 and 1 from before it left must not show up.
    want = expected_frames("agent_1", 1, (3,), 3, initial)
    want = [f + 20 * 4 if f.any() else f for f in want]
    assert np.array_equal(obs["agent_1"], np.concatenate(want))


@pytest.mark.parametrize("initial", INITIALS)
def test_aec_agent_leaving_and_coming_back_starts_fresh(initial):
    env = FrameStackV3(parallel_to_aec(RejoinParallel()), 3, initial=initial)
    env.reset(seed=0)
    for _ in range(4):
        for _agent in list(env.agents):
            env.step(0)
    # frame 4, agent_1 is back and has not had a turn since
    assert env.agents == AGENTS and env.agent_selection == "agent_0"
    assert "agent_1" not in env._history
    want = expected_frames("agent_1", 0, (3,), 3, initial)
    want = [f + 20 * 4 if f.any() else f for f in want]
    assert np.array_equal(env.observe("agent_1"), np.concatenate(want))


def test_returned_observation_is_not_aliased():
    env = FrameStackV3(DummyAEC(), 2)
    env.reset(seed=0)
    obs = env.observe("agent_0")
    obs[:] = 99.0
    assert_stack(env.observe("agent_0"), "agent_0", 0, (3,), -1, 2, "first_obs")


def test_source_observation_is_not_aliased():
    class MutatingEnv(DummyAEC):
        def __init__(self):
            super().__init__()
            self.buffer = np.zeros(3, dtype=np.float32)

        def observe(self, agent):
            self.buffer[:] = frame_obs(agent, self.frame, (3,))
            return self.buffer

    env = FrameStackV3(MutatingEnv(), 2)
    env.reset(seed=0)
    env.step(0)
    env.step(0)  # one full cycle
    assert_stack(env.observe("agent_0"), "agent_0", 1, (3,), -1, 2, "first_obs")


@pytest.mark.parametrize(
    "space, match",
    [
        (Dict({"a": Discrete(2)}), "Dict"),
        (MultiDiscrete([2, 2]), "MultiDiscrete"),
        (Box(0, 1, (1, 1, 1, 1)), "1, 2 or 3"),
        (Box(0, 1, ()), "1, 2 or 3"),
    ],
)
def test_rejects_unsupported_spaces(space, match):
    class Env(DummyAEC):
        def observation_space(self, agent):
            return space

    class ParEnv(DummyParallel):
        def observation_space(self, agent):
            return space

    with pytest.raises(ValueError, match=match):
        FrameStackV3(Env(), 2)
    with pytest.raises(ValueError, match=match):
        FrameStackV3(ParEnv(), 2)


def test_rejects_dict_observations_from_generated_agents():
    # This env has no possible_agents, so the check has to happen at reset.
    env = FrameStackV3(generated_agents_env_action_mask_obs_v0.env(), 3)
    with pytest.raises(ValueError, match="Dict"):
        env.reset(seed=0)


@pytest.mark.parametrize("stack_size", [0, -1, 1.5, "2", None, True])
def test_rejects_bad_stack_size(stack_size):
    with pytest.raises((TypeError, ValueError)):
        FrameStackV3(DummyAEC(), stack_size)
    with pytest.raises((TypeError, ValueError)):
        FrameStackV3(DummyParallel(), stack_size)


@pytest.mark.parametrize("stack_dim", [1, 2, -2, -1.0, None, True, False])
def test_rejects_bad_stack_dim(stack_dim):
    with pytest.raises(ValueError, match="stack_dim"):
        FrameStackV3(DummyAEC(), 2, stack_dim)
    with pytest.raises(ValueError, match="stack_dim"):
        FrameStackV3(DummyParallel(), 2, stack_dim)


@pytest.mark.parametrize("initial", ["first", "zero", None, "v1"])
def test_rejects_bad_initial(initial):
    with pytest.raises(ValueError, match="initial"):
        FrameStackV3(DummyAEC(), 2, initial=initial)
    with pytest.raises(ValueError, match="initial"):
        FrameStackV3(DummyParallel(), 2, initial=initial)


def test_one_wrapper_for_both_apis():
    aec = FrameStackV3(DummyAEC(), 2)
    par = FrameStackV3(DummyParallel(), 2)
    assert isinstance(aec, FrameStackV3) and isinstance(aec, AECEnv)
    assert not isinstance(aec, ParallelEnv)
    assert isinstance(par, FrameStackV3) and isinstance(par, ParallelEnv)
    assert not isinstance(par, AECEnv)


@pytest.mark.parametrize("env", [None, object(), "env", DummyAEC])
def test_rejects_things_that_are_not_envs(env):
    with pytest.raises(TypeError, match="AECEnv or a ParallelEnv"):
        FrameStackV3(env, 2)


@pytest.mark.parametrize("make_env", [DummyAEC, DummyParallel])
def test_pickle_round_trip(make_env):
    env = FrameStackV3(make_env(), 3, 0, "zeros")
    copy = pickle.loads(pickle.dumps(env))
    assert type(copy) is type(env)
    assert (copy.stack_size, copy.stack_dim, copy.initial) == (3, 0, "zeros")
    assert copy.observation_space("agent_0") == env.observation_space("agent_0")


def test_str():
    assert str(FrameStackV3(DummyAEC(), 2)).startswith("FrameStackV3<")
    assert str(FrameStackV3(DummyParallel(), 2)).startswith("FrameStackV3<")


@pytest.mark.parametrize("initial", INITIALS)
@pytest.mark.parametrize("stack_dim", STACK_DIMS)
@pytest.mark.parametrize("dims", SHAPES)
def test_aec_api(dims, stack_dim, initial):
    env = DummyAEC(SHAPES[dims][stack_dim])
    api_test(FrameStackV3(env, 3, stack_dim, initial), num_cycles=10)


@pytest.mark.parametrize("initial", INITIALS)
def test_aec_api_discrete_and_positive_low(initial):
    api_test(FrameStackV3(DiscreteAEC(start=2), 3, initial=initial), num_cycles=10)
    api_test(FrameStackV3(PositiveLowAEC(), 3, initial=initial), num_cycles=10)


def test_aec_api_on_converted_parallel_env():
    api_test(FrameStackV3(parallel_to_aec(LeavingParallel()), 3), num_cycles=10)


@pytest.mark.parametrize("initial", INITIALS)
def test_aec_api_with_generated_agents(initial):
    # agents come and go mid-episode
    api_test(
        FrameStackV3(generated_agents_env_v0.env(), 2, initial=initial), num_cycles=20
    )


@pytest.mark.parametrize("initial", INITIALS)
@pytest.mark.parametrize("stack_dim", STACK_DIMS)
@pytest.mark.parametrize("dims", SHAPES)
def test_parallel_api(dims, stack_dim, initial):
    env = DummyParallel(SHAPES[dims][stack_dim])
    parallel_api_test(FrameStackV3(env, 3, stack_dim, initial), num_cycles=10)


def test_parallel_api_with_leaving_agents():
    parallel_api_test(FrameStackV3(LeavingParallel(), 3), num_cycles=10)
