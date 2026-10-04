from __future__ import annotations

import numpy as np

from pettingzoo import make
from pettingzoo.classic.leduc_holdem_v5 import env, raw_env
from pettingzoo.test.api_test import api_test
from pettingzoo.test.render_test import render_test
from pettingzoo.test.seed_test import seed_test


def test_leduc_holdem_v5_api():
    api_test(env(), num_cycles=100)


def test_leduc_holdem_v5_seed():
    seed_test(env, num_cycles=100)


def test_leduc_holdem_v5_render():
    render_test(env)


def test_leduc_holdem_v5_is_registered():
    game = make("aec", "classic/leduc_holdem-v5")
    game.reset(seed=42)
    assert game.unwrapped.metadata["name"] == "leduc_holdem_v5"
    game.close()


def test_observation_hides_opponent_private_card():
    game = raw_env()
    game.reset(seed=42)

    observation = game.observe("player_0")["observation"]
    private_card = game.leduc_env.game_state.private_card(0)

    assert observation.shape == (16,)
    assert observation[:2].sum() == 1
    assert observation[2:8].sum() == 1
    assert observation[2 + private_card] == 1
    assert observation[8:14].sum() == 0
    assert observation[14:16].sum() == 2
    assert np.isin(observation, (0, 1)).all()


def test_terminal_rewards_keep_documented_scale():
    game = raw_env()
    game.reset(seed=7)

    for _ in range(100):
        agent = game.agent_selection
        observation = game.observe(agent)
        if game.terminations[agent] or game.truncations[agent]:
            game.step(None)
            continue
        action = game.action_space(agent).sample(observation["action_mask"])
        game.step(action)
        if any(game.terminations.values()):
            break

    assert any(game.terminations.values())
    expected = game.leduc_env.game_state.returns()
    assert np.allclose(
        [game.rewards[agent] for agent in game.possible_agents],
        np.asarray(expected) * 0.5,
    )


def test_valid_two_round_game_is_not_truncated_early():
    game = raw_env()
    game.reset(seed=1)

    for _ in range(30):
        agent = game.agent_selection
        if game.terminations[agent] or game.truncations[agent]:
            break
        action_mask = game.observe(agent)["action_mask"]
        action = 2 if action_mask[2] else 1
        game.step(action)

    assert all(game.terminations.values())
    assert not any(game.truncations.values())
    assert game.leduc_env.game_state.is_terminal()
