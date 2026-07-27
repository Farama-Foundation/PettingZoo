"""Regression tests for the deterministic KAZ tutorial policy."""

from __future__ import annotations

from types import SimpleNamespace

import numpy as np
import pytest

from tutorials.SB3.kaz import predictive_kaz_policy as policy


def _observation(*zombies: tuple[float, float, float]) -> np.ndarray:
    current = np.zeros(11, dtype=np.float64)
    current[5] = 1.0
    current[9] = 1.0

    rows = [current]
    for distance, relative_x, relative_y in zombies:
        zombie = np.zeros(11, dtype=np.float64)
        zombie[0] = 1.0
        zombie[6] = distance
        zombie[7] = relative_x
        zombie[8] = relative_y
        rows.append(zombie)
    return np.stack(rows)


def test_zero_distance_zombie_remains_active() -> None:
    observation = _observation((0.0, 0.0, 0.0))

    zombies = policy.active_zombies(observation)

    assert len(zombies) == 1
    np.testing.assert_allclose(zombies[0], observation[1])


def test_surviving_role_agent_targets_bottom_threat() -> None:
    observation = _observation(
        (0.2, 0.0, 0.9),
        (0.1, 0.0, 0.7),
    )

    target = policy.target_for_agent(
        observation,
        "archer_1",
        policy.PolicyParams(),
        role_rank=0,
    )

    assert target is not None
    assert target[8] == pytest.approx(0.9)


def test_live_role_rank_splits_targets() -> None:
    observation = _observation(
        (0.2, 0.0, 0.9),
        (0.1, 0.0, 0.7),
    )

    first = policy.target_for_agent(
        observation,
        "archer_0",
        policy.PolicyParams(),
        role_rank=0,
    )
    second = policy.target_for_agent(
        observation,
        "archer_1",
        policy.PolicyParams(),
        role_rank=1,
    )

    assert first is not None
    assert second is not None
    assert first[8] == pytest.approx(0.9)
    assert second[8] == pytest.approx(0.7)


def test_run_episode_closes_environment_on_policy_error(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    closed = False

    class ActionSpace:
        def seed(self, _: int) -> None:
            pass

    class FakeEnv:
        possible_agents = ["archer_0"]
        agents = ["archer_0"]
        terminations = {"archer_0": False}
        truncations = {"archer_0": False}
        unwrapped = SimpleNamespace(frames=0)

        def reset(self, *, seed: int) -> None:
            pass

        def action_space(self, agent: str) -> ActionSpace:
            return ActionSpace()

        def agent_iter(self):
            yield "archer_0"

        def last(self):
            return _observation((0.1, 0.0, 0.8)), 0.0, False, False, {}

        def step(self, action: int | None) -> None:
            pass

        def close(self) -> None:
            nonlocal closed
            closed = True

    monkeypatch.setattr(policy, "make", lambda *args, **kwargs: FakeEnv())
    monkeypatch.setattr(
        policy,
        "policy_action",
        lambda *args, **kwargs: (_ for _ in ()).throw(RuntimeError("boom")),
    )

    with pytest.raises(RuntimeError, match="boom"):
        policy.run_episode(seed=7)

    assert closed


def test_run_episode_rejects_nonpositive_frame_stride() -> None:
    with pytest.raises(ValueError, match="frame_stride"):
        policy.run_episode(seed=0, frame_stride=0)


def test_registry_environment_smoke() -> None:
    result = policy.run_episode(seed=0, max_cycles=1, max_zombies=1)

    assert result.cycles == 1
