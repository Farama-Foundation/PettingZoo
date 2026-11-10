from __future__ import annotations

import warnings

import numpy as np
import pytest
from gymnasium.spaces import Box, Discrete, MultiBinary, MultiDiscrete

from pettingzoo.test import api_test, parallel_api_test
from pettingzoo.utils.wrappers import NanNoopParallelV1, NanNoopV1

from .scale_action_test import DummyAEC, DummyParallel


@pytest.fixture(params=[(NanNoopV1, DummyAEC), (NanNoopParallelV1, DummyParallel)])
def api(request):
    return request.param


def step_actions(env, actions):
    if isinstance(env, NanNoopV1):
        for agent, action in actions.items():
            assert env.agent_selection == agent
            env.step(action)
    else:
        env.step(actions)


@pytest.mark.parametrize(
    "space,noop,nan_action,clean",
    [
        (Discrete(4), 2, np.nan, 1),
        (Box(-1.0, 1.0, (), np.float64), np.array(0.5), np.nan, np.array(-0.5)),
        (
            Box(-1.0, 1.0, (3,), np.float32),
            np.array([0.25, 0.5, 0.75], dtype=np.float32),
            np.array([0.0, np.nan, 1.0], dtype=np.float32),
            np.array([-0.5, 0.0, 0.5], dtype=np.float32),
        ),
        (
            MultiDiscrete([3, 4]),
            np.array([1, 2]),
            np.array([np.nan, 1]),
            np.array([2, 3]),
        ),
        (
            MultiBinary(2),
            np.array([0, 1], dtype=np.int8),
            np.array([0, np.nan]),
            np.array([1, 0]),
        ),
    ],
)
def test_replaces_only_nan_actions(api, space, noop, nan_action, clean):
    wrapper, inner = api
    env = wrapper(inner(lambda agent: space), noop)
    env.reset()
    actions = {"agent_0": nan_action, "agent_1": clean}

    with pytest.warns(UserWarning, match="NaN"):
        step_actions(env, actions)

    received = env.unwrapped.received
    np.testing.assert_array_equal(received["agent_0"], noop)
    assert space.contains(received["agent_0"])
    assert received["agent_1"] is clean
    assert actions["agent_0"] is nan_action
    assert env.action_space("agent_0") is space
    assert env.observation_space("agent_0") is env.unwrapped.observation_space(
        "agent_0"
    )


def test_each_agent_uses_its_own_space(api):
    wrapper, inner = api
    env = wrapper(inner(lambda agent: Discrete(3 if agent == "agent_0" else 5)), 2)
    env.reset()
    with pytest.warns(UserWarning, match="NaN") as recorded:
        step_actions(env, dict.fromkeys(env.agents, np.nan))
    assert len(recorded) == 2
    assert env.unwrapped.received == {"agent_0": 2, "agent_1": 2}


@pytest.mark.parametrize(
    "space,noop",
    [
        (Discrete(2), 2),
        (Discrete(2), None),
        (Box(1.0, 2.0, (2,), np.float32), np.zeros(2, dtype=np.float32)),
        (Box(-1.0, 1.0, (2,), np.float32), np.zeros(3, dtype=np.float32)),
        (Box(-1.0, 1.0, (2,), np.float32), np.zeros(2, dtype=np.float64)),
        (Box(-1.0, 1.0, (2,), np.float32), np.full(2, np.nan, dtype=np.float32)),
    ],
)
def test_invalid_noop_is_rejected(api, space, noop):
    wrapper, inner = api
    with pytest.raises(ValueError, match=r"no-op.*agent_0"):
        wrapper(inner(lambda agent: space), noop)


def test_noop_must_fit_every_possible_agent(api):
    wrapper, inner = api
    with pytest.raises(ValueError, match=r"no-op.*agent_1"):
        wrapper(inner(lambda agent: Discrete(5 if agent == "agent_0" else 2)), 2)


def test_noop_is_checked_for_agents_without_possible_agents(api):
    wrapper, inner = api
    base = inner(lambda agent: Discrete(2))
    base.reset()
    del base.possible_agents
    env = wrapper(base, 2)
    with pytest.raises(ValueError, match=r"no-op.*agent_0"):
        step_actions(env, {"agent_0": np.nan})
    assert not base.received


def test_no_nan_actions_are_unchanged_even_if_outside_space(api):
    wrapper, inner = api
    env = wrapper(inner(lambda agent: Discrete(2)), 0)
    env.reset()
    with warnings.catch_warnings():
        warnings.simplefilter("error")
        step_actions(env, {"agent_0": 10, "agent_1": np.inf})
    assert env.unwrapped.received == {"agent_0": 10, "agent_1": np.inf}


@pytest.mark.parametrize("done_flag", ["terminations", "truncations"])
def test_aec_dead_step_preserves_none(done_flag):
    env = NanNoopV1(DummyAEC(lambda agent: Discrete(2)), 0)
    env.reset()
    getattr(env.unwrapped, done_flag)["agent_0"] = True
    with warnings.catch_warnings():
        warnings.simplefilter("error")
        env.step(None)
    assert env.agents == ["agent_1"]
    assert not env.unwrapped.received


def test_replacement_arrays_are_independent(api):
    wrapper, inner = api
    noop = np.array([0.25, 0.5, 0.75], dtype=np.float32)
    env = wrapper(inner(), noop)
    env.reset()
    with pytest.warns(UserWarning, match="NaN"):
        step_actions(env, dict.fromkeys(env.agents, np.nan))
    received = env.unwrapped.received
    received["agent_0"][0] = 1.0
    np.testing.assert_array_equal(received["agent_1"], noop)
    assert noop[0] == 0.25
    env.reset()
    with pytest.warns(UserWarning, match="NaN"):
        step_actions(env, dict.fromkeys(env.agents, np.nan))
    np.testing.assert_array_equal(env.unwrapped.received["agent_0"], noop)


def test_aec_api():
    api_test(NanNoopV1(DummyAEC(lambda agent: Discrete(3)), 1), 5)


def test_parallel_api():
    parallel_api_test(NanNoopParallelV1(DummyParallel(lambda agent: Discrete(3)), 1), 5)


def test_str(api):
    wrapper, inner = api
    env = wrapper(inner(lambda agent: Discrete(3)), 1)
    assert str(env) == f"{wrapper.__name__}<{env.unwrapped!s}>"
