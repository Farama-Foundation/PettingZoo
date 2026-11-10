"""Episode endings in the Box2D Multiwalker environment."""

import numpy as np
import pytest

pytest.importorskip("Box2D")

from pettingzoo import make


def step_world(env, mode):
    if mode == "parallel":
        _, _, terminations, truncations, _ = env.step(
            {agent: np.zeros(4, dtype=np.float32) for agent in env.agents}
        )
        return terminations, truncations
    for _ in range(len(env.agents)):
        env.step(np.zeros(4, dtype=np.float32))
    return env.terminations.copy(), env.truncations.copy()


@pytest.mark.parametrize("mode", ["aec", "parallel"])
@pytest.mark.parametrize("max_cycles", [1, 3])
@pytest.mark.parametrize("seed", [0, 7])
def test_time_limit_truncates_without_terminating(mode, max_cycles, seed):
    env = make(mode, "sisl/multiwalker", max_cycles=max_cycles)
    try:
        env.reset(seed=seed)
        for cycle in range(1, max_cycles + 1):
            terminations, truncations = step_world(env, mode)
            assert not any(terminations.values())
            assert all(value == (cycle == max_cycles) for value in truncations.values())
        if mode == "aec":
            # Truncated agents still get their final observation/reward before
            # the normal dead-step cleanup removes them.
            while env.agents:
                observation, _, terminated, truncated, _ = env.last()
                assert observation is not None
                assert truncated and not terminated
                env.step(None)
        assert env.agents == []
        env.reset(seed=seed)
        assert env.agents == env.possible_agents
        assert not any(env.unwrapped.terminations.values())
        assert not any(env.unwrapped.truncations.values())
    finally:
        env.close()


@pytest.mark.parametrize("mode", ["aec", "parallel"])
@pytest.mark.parametrize("failure_cycle", [1, 3])
def test_game_over_still_terminates_at_or_before_the_time_limit(mode, failure_cycle):
    env = make(mode, "sisl/multiwalker", max_cycles=3)
    try:
        env.reset(seed=0)
        for cycle in range(1, failure_cycle + 1):
            if cycle == failure_cycle:
                # The package contact listener sets this flag on terrain contact.
                env.unwrapped.env.game_over = True
            terminations, truncations = step_world(env, mode)
        assert all(terminations.values())
        assert all(value == (failure_cycle == 3) for value in truncations.values())
    finally:
        env.close()


def test_time_limit_truncates_survivors_after_an_individual_fall():
    env = make("parallel", "sisl/multiwalker", max_cycles=2, terminate_on_fall=False)
    try:
        env.reset(seed=0)
        # The hull contact listener sets this flag when an individual walker falls.
        env.unwrapped.env.fallen_walkers[0] = True
        terminations, truncations = step_world(env, "parallel")
        assert terminations == {"walker_0": True, "walker_1": False, "walker_2": False}
        assert not any(truncations.values())
        assert env.agents == ["walker_1", "walker_2"]
        terminations, truncations = step_world(env, "parallel")
        assert terminations == {"walker_1": False, "walker_2": False}
        assert truncations == {"walker_1": True, "walker_2": True}
        assert env.agents == []
    finally:
        env.close()
