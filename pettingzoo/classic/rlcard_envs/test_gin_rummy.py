"""Tests for the gin_rummy environment.

Regression tests for https://github.com/Farama-Foundation/PettingZoo/issues/1312:
calling ``reset(seed=...)`` rebuilt the underlying RLCard env and discarded the
custom payoff scorer, silently reverting the configured ``knock_reward`` /
``gin_reward`` to RLCard's defaults (0.2 / 1.0).
"""

from __future__ import annotations

import random

import numpy as np

from pettingzoo.classic import gin_rummy_v5
from pettingzoo.test import seed_test

# Action ids that end a hand (gin, or any of the 52 knock actions).
GIN_ACTION = 5
KNOCK_ACTIONS = range(58, 110)


def test_payoff_override_survives_seeded_reset():
    """Ensure the custom payoff scorer survives a seeded reset."""
    env = gin_rummy_v5.env(knock_reward=0.5, gin_reward=1.0)

    env.reset()  # no seed: override installed in __init__
    raw = env.unwrapped
    assert raw.env.game.judge.scorer.get_payoff == raw._get_payoff

    env.reset(seed=42)  # seeded: env is rebuilt, override must be re-applied
    assert raw.env.game.judge.scorer.get_payoff == raw._get_payoff


def test_configured_knock_reward_used_in_seeded_game():
    """Ensure a seeded knock pays the configured reward, not RLCard's 0.2."""
    knock_reward = 0.5

    def finisher_policy(mask, rng):
        legal = np.flatnonzero(mask).tolist()
        finishers = [a for a in legal if a == GIN_ACTION or a in KNOCK_ACTIONS]
        return min(finishers) if finishers else rng.choice(legal)

    saw_knock = False
    for seed in range(50):
        env = gin_rummy_v5.env(knock_reward=knock_reward, gin_reward=1.0)
        env.reset(seed=seed)
        raw = env.unwrapped
        rng = random.Random(seed)
        for _ in env.agent_iter(max_iter=10_000):
            obs, _, term, trunc, _ = env.last()
            if term or trunc:
                going_out = raw.env.game.round.going_out_action
                if type(going_out).__name__ == "KnockAction":
                    saw_knock = True
                    assert max(env.rewards.values()) == knock_reward
                env.step(None)
                break
            env.step(finisher_policy(obs["action_mask"], rng))

    assert saw_knock, "test did not exercise a knock ending; cannot validate reward"


def test_seeding_is_deterministic():
    """Run PettingZoo's determinism check for gin_rummy."""
    seed_test(gin_rummy_v5.env)
