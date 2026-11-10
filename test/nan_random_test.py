from __future__ import annotations

import warnings

import numpy as np
import pytest
from gymnasium.spaces import Box, Dict, Discrete, MultiBinary, MultiDiscrete

from pettingzoo.test import api_test, parallel_api_test
from pettingzoo.utils.wrappers import NanRandomParallelV1, NanRandomV1

from .scale_action_test import OBS, OBS_SPACE, DummyAEC, DummyParallel

N_ACTIONS = 6
MASKS = {
    "agent_0": np.array([0, 1, 0, 1, 0, 0], dtype=np.int8),
    "agent_1": np.array([0, 0, 0, 0, 0, 1], dtype=np.int8),
}
MASKED_OBS_SPACE = Dict(
    {"observation": OBS_SPACE, "action_mask": Box(0, 1, (N_ACTIONS,), np.int8)}
)


def discrete(agent):
    return Discrete(N_ACTIONS)


class MaskedAEC(DummyAEC):
    """A DummyAEC whose agents carry an action mask in their observation or info."""

    def __init__(self, obs_masks=MASKS, info_masks=None, space_fn=discrete):
        super().__init__(space_fn)
        self.obs_masks = obs_masks
        self.info_masks = info_masks

    def observation_space(self, agent):
        if self.obs_masks is None:
            return OBS_SPACE
        return MASKED_OBS_SPACE

    def observe(self, agent):
        if self.obs_masks is None:
            return OBS
        return {"observation": OBS, "action_mask": self.obs_masks[agent]}

    def reset(self, seed=None, options=None):
        super().reset(seed, options)
        if self.info_masks is not None:
            self.infos = {a: {"action_mask": self.info_masks[a]} for a in self.agents}


class MaskedParallel(DummyParallel):
    """A DummyParallel whose agents carry an action mask in their observation or info."""

    def __init__(self, obs_masks=MASKS, info_masks=None, space_fn=discrete):
        super().__init__(space_fn)
        self.obs_masks = obs_masks
        self.info_masks = info_masks

    def observation_space(self, agent):
        if self.obs_masks is None:
            return OBS_SPACE
        return MASKED_OBS_SPACE

    def _with_masks(self, observations, infos):
        if self.obs_masks is not None:
            observations = {
                a: {"observation": obs, "action_mask": self.obs_masks[a]}
                for a, obs in observations.items()
            }
        if self.info_masks is not None:
            infos = {a: {"action_mask": self.info_masks[a]} for a in infos}
        return observations, infos

    def reset(self, seed=None, options=None):
        return self._with_masks(*super().reset(seed, options))

    def step(self, actions):
        observations, rewards, terminations, truncations, infos = super().step(actions)
        observations, infos = self._with_masks(observations, infos)
        return observations, rewards, terminations, truncations, infos


@pytest.fixture(
    params=[
        (NanRandomV1, DummyAEC, MaskedAEC),
        (NanRandomParallelV1, DummyParallel, MaskedParallel),
    ],
    ids=["aec", "parallel"],
)
def api(request):
    return request.param


def step_actions(env, actions):
    if isinstance(env, NanRandomV1):
        for agent, action in actions.items():
            assert env.agent_selection == agent
            env.step(action)
    else:
        env.step(actions)


def nan_step(env):
    """Sends a NaN for every agent and returns the actions the environment got."""
    with pytest.warns(UserWarning, match="NaN") as recorded:
        step_actions(env, dict.fromkeys(env.agents, np.nan))
    assert len(recorded) == len(env.unwrapped.received)
    return dict(env.unwrapped.received)


@pytest.mark.parametrize(
    "space,nan_action,clean",
    [
        (Discrete(4, start=2), np.nan, 3),
        (Box(-1.0, 1.0, (), np.float64), np.nan, np.array(-0.5)),
        (
            Box(-1.0, 1.0, (3,), np.float32),
            np.array([0.0, np.nan, 1.0], dtype=np.float32),
            np.array([-0.5, 0.0, 0.5], dtype=np.float32),
        ),
        (MultiDiscrete([3, 4]), np.array([np.nan, 1]), np.array([2, 3])),
        (MultiBinary(2), np.array([0, np.nan]), np.array([1, 0])),
    ],
)
def test_replaces_only_nan_actions(api, space, nan_action, clean):
    wrapper, inner, _ = api
    env = wrapper(inner(lambda agent: space))
    env.reset(seed=0)
    actions = {"agent_0": nan_action, "agent_1": clean}

    with pytest.warns(UserWarning, match="NaN") as recorded:
        step_actions(env, actions)

    assert len(recorded) == 1
    received = env.unwrapped.received
    assert space.contains(received["agent_0"])
    assert received["agent_1"] is clean
    assert actions["agent_0"] is nan_action
    assert env.action_space("agent_0") is space


def test_each_agent_samples_its_own_space(api):
    wrapper, inner, _ = api
    spaces = {"agent_0": Discrete(2), "agent_1": Discrete(3, start=10)}
    env = wrapper(inner(lambda agent: spaces[agent]))
    env.reset(seed=0)
    seen = {agent: set() for agent in spaces}
    for _ in range(3):
        for agent, action in nan_step(env).items():
            seen[agent].add(int(action))
    assert seen["agent_0"] <= {0, 1}
    assert seen["agent_1"] <= {10, 11, 12}


@pytest.mark.parametrize("location", ["observation", "info"])
def test_masked_replacements_are_allowed_actions(api, location):
    wrapper, _, masked = api
    if location == "observation":
        inner = masked(obs_masks=MASKS)
    else:
        inner = masked(obs_masks=None, info_masks=MASKS)
    for seed in range(20):
        env = wrapper(inner)
        env.reset(seed=seed)
        for agent, action in nan_step(env).items():
            assert MASKS[agent][action] == 1


def test_masked_replacements_cover_every_allowed_action(api):
    wrapper, _, masked = api
    seen = set()
    for seed in range(50):
        env = wrapper(masked())
        env.reset(seed=seed)
        seen.add(int(nan_step(env)["agent_0"]))
    assert seen == {1, 3}


def test_observation_mask_takes_precedence_over_info_mask(api):
    wrapper, _, masked = api
    obs_masks = {agent: np.eye(N_ACTIONS, dtype=np.int8)[0] for agent in MASKS}
    info_masks = {agent: np.eye(N_ACTIONS, dtype=np.int8)[5] for agent in MASKS}
    env = wrapper(masked(obs_masks=obs_masks, info_masks=info_masks))
    env.reset(seed=0)
    assert nan_step(env) == {"agent_0": 0, "agent_1": 0}


def test_parallel_uses_the_latest_mask():
    inner = MaskedParallel(obs_masks={a: np.ones(N_ACTIONS, np.int8) for a in MASKS})
    env = NanRandomParallelV1(inner)
    env.reset(seed=0)
    env.step({"agent_0": 0, "agent_1": 0})
    # Masks change after the step; the wrapper must use the ones it just returned.
    inner.obs_masks = MASKS
    env.step({"agent_0": 0, "agent_1": 0})
    for _ in range(5):
        for agent, action in nan_step(env).items():
            assert MASKS[agent][action] == 1


def test_masked_replacement_respects_space_start(api):
    wrapper, _, masked = api
    mask = np.array([0, 1, 0], dtype=np.int8)
    env = wrapper(
        masked(
            obs_masks=dict.fromkeys(MASKS, mask),
            space_fn=lambda a: Discrete(3, start=5),
        )
    )
    env.reset(seed=0)
    for action in nan_step(env).values():
        assert action == 6


def test_boolean_mask_is_accepted(api):
    wrapper, _, masked = api
    env = wrapper(masked(obs_masks={a: m.astype(bool) for a, m in MASKS.items()}))
    env.reset(seed=0)
    for agent, action in nan_step(env).items():
        assert MASKS[agent][action] == 1


@pytest.mark.parametrize(
    "mask,match",
    [
        (np.zeros(N_ACTIONS, dtype=np.int8), "allows no actions"),
        (np.ones(N_ACTIONS - 1, dtype=np.int8), "shape"),
        (np.full(N_ACTIONS, 2, dtype=np.int8), "only 0 and 1"),
        (np.full(N_ACTIONS, 0.5), "only 0 and 1"),
        (np.ones((2, N_ACTIONS), dtype=np.int8), "shape"),
    ],
)
def test_malformed_mask_is_rejected(api, mask, match):
    wrapper, _, masked = api
    env = wrapper(masked(obs_masks=dict.fromkeys(MASKS, mask)))
    env.reset(seed=0)
    with pytest.raises(ValueError, match=match):
        step_actions(env, {"agent_0": np.nan})
    assert "agent_0" not in env.unwrapped.received


def test_mask_on_non_discrete_space_is_rejected(api):
    wrapper, _, masked = api
    env = wrapper(
        masked(
            obs_masks=None, info_masks=MASKS, space_fn=lambda a: MultiDiscrete([2, 3])
        )
    )
    env.reset(seed=0)
    with pytest.raises(ValueError, match="only Discrete"):
        step_actions(env, {"agent_0": np.array([np.nan, 0])})


def test_masked_env_without_nan_is_unchanged(api):
    wrapper, _, masked = api
    env = wrapper(masked())
    env.reset(seed=0)
    with warnings.catch_warnings():
        warnings.simplefilter("error")
        # Valid actions pass through even when the mask forbids them: this
        # wrapper only replaces NaNs.
        step_actions(env, {"agent_0": 0, "agent_1": 0})
    assert env.unwrapped.received == {"agent_0": 0, "agent_1": 0}


def replacement_sequence(env, seed, steps=3):
    env.reset(seed=seed)
    return [nan_step(env) for _ in range(steps)]


def test_seeded_reset_is_reproducible(api):
    wrapper, inner, _ = api
    env = wrapper(inner(lambda agent: Discrete(10_000)))
    first = replacement_sequence(env, seed=42)
    # The wrapped environment's own action space RNG does not affect the result.
    env.unwrapped.action_space("agent_0").sample()
    assert replacement_sequence(env, seed=42) == first
    assert replacement_sequence(env, seed=43) != first


def test_seeded_masked_reset_is_reproducible(api):
    wrapper, _, masked = api
    mask = np.ones(N_ACTIONS, dtype=np.int8)
    env = wrapper(masked(obs_masks=dict.fromkeys(MASKS, mask)))
    assert replacement_sequence(env, seed=7) == replacement_sequence(env, seed=7)


def test_replacement_does_not_advance_the_environment_rng(api):
    wrapper, inner, _ = api
    env = wrapper(inner(lambda agent: Discrete(10)))
    env.reset(seed=0)
    space = env.unwrapped.action_space("agent_0")
    state = space.np_random.bit_generator.state
    nan_step(env)
    assert space.np_random.bit_generator.state == state


def test_aec_dead_agent_none_passes_through():
    env = NanRandomV1(DummyAEC(discrete))
    env.reset(seed=0)
    with pytest.warns(UserWarning, match="NaN"):
        while not all(env.terminations.values()):
            env.step(np.nan)
    with warnings.catch_warnings():
        warnings.simplefilter("error")
        while env.agents:
            env.step(None)


def test_aec_rejects_parallel_env():
    with pytest.raises(AssertionError, match="NanRandomParallelV1"):
        NanRandomV1(DummyParallel())


def test_str(api):
    wrapper, inner, _ = api
    assert str(wrapper(inner())).startswith(f"{wrapper.__name__}<")


def test_aec_api():
    api_test(NanRandomV1(MaskedAEC()), 5)


def test_parallel_api():
    parallel_api_test(
        NanRandomParallelV1(MaskedParallel(obs_masks=None, info_masks=MASKS)), 5
    )
