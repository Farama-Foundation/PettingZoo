from __future__ import annotations

import json
import pickle

import numpy as np
import pytest

from pettingzoo import make, spec
from pettingzoo.classic.rlcard_envs.texas_holdem import env, raw_env
from pettingzoo.test import api_test, seed_test

pytest.importorskip("pyspiel")


@pytest.mark.parametrize("num_players", [2, 3, 4])
def test_pettingzoo_api(num_players: int):
    api_test(env(num_players=num_players), num_cycles=1_000)


@pytest.mark.parametrize("num_players", [2, 3, 4])
def test_pettingzoo_seed_determinism(num_players: int):
    seed_test(lambda: env(num_players=num_players), num_cycles=500)


@pytest.mark.parametrize(
    ("num_players", "observation_size"), [(2, 108), (3, 110), (4, 112)]
)
def test_openspiel_spaces_and_observation_layout(
    num_players: int, observation_size: int
):
    env = raw_env(num_players=num_players)
    env.reset(seed=42)

    assert env.action_space("player_0").n == 3
    assert env.observation_space("player_0")["observation"].shape == (observation_size,)

    state = json.loads(env.texas_holdem_env.game_state.to_json())
    for player_id, agent in enumerate(env.possible_agents):
        observation = env.observe(agent)["observation"]
        np.testing.assert_array_equal(
            observation[:num_players], np.eye(num_players)[player_id]
        )
        np.testing.assert_array_equal(
            observation[-num_players:], state["player_contributions"]
        )

    acting_agent = env.agent_selection
    for player_id, agent in enumerate(env.possible_agents):
        expected_legal_actions = (
            env.texas_holdem_env.game_state.legal_actions(player_id)
            if agent == acting_agent
            else []
        )
        actual_legal_actions = np.flatnonzero(
            env.observe(agent)["action_mask"]
        ).tolist()
        assert actual_legal_actions == expected_legal_actions

    env.close()


@pytest.mark.parametrize("num_players", [1, 5])
def test_rejects_unsupported_player_counts(num_players: int):
    with pytest.raises(ValueError, match="between 2 and 4 players"):
        raw_env(num_players=num_players)


def test_seed_controls_cards_and_blind_rotation():
    env_1 = raw_env(num_players=4)
    env_2 = raw_env(num_players=4)

    env_1.reset(seed=42)
    env_2.reset(seed=42)

    state_1 = json.loads(env_1.texas_holdem_env.game_state.to_json())
    state_2 = json.loads(env_2.texas_holdem_env.game_state.to_json())
    assert state_1 == state_2
    assert env_1.agent_selection == env_2.agent_selection
    assert sorted(state_1["blinds"]) == [0, 0, 1, 2]

    env_1.close()
    env_2.close()


def test_standard_limit_holdem_configuration():
    env = raw_env(num_players=2)

    # This is OpenSpiel's canonical HULH game, scaled from 5/10 chips to
    # PettingZoo's historic 1/2-chip stakes and with either seat as dealer.
    for small_blind in range(2):
        config = env._game_config(small_blind)
        assert config["betting"] == "limit"
        assert config["bettingAbstraction"] == "fcpa"
        assert config["raiseSize"] == "2 2 4 4"
        assert config["maxRaises"] == "3 4 4 4"
        assert config["numBoardCards"] == "0 3 1 1"

        blinds = [int(blind) for blind in config["blind"].split()]
        first_players = [int(player) - 1 for player in config["firstPlayer"].split()]
        big_blind = (small_blind + 1) % 2
        assert blinds[small_blind] == 1
        assert blinds[big_blind] == 2
        assert first_players == [small_blind, big_blind, big_blind, big_blind]

    env.close()


def test_pickled_environment_recreates_seeded_game():
    env_1 = raw_env(num_players=4, render_mode="rgb_array", screen_height=300)
    env_2 = pickle.loads(pickle.dumps(env_1))

    env_1.reset(seed=42)
    env_2.reset(seed=42)

    assert env_1.agent_selection == env_2.agent_selection
    assert env_1._config == env_2._config
    assert (
        env_1.texas_holdem_env.game_state.to_json()
        == env_2.texas_holdem_env.game_state.to_json()
    )
    np.testing.assert_array_equal(env_1.render(), env_2.render())

    env_1.close()
    env_2.close()


@pytest.mark.parametrize("num_players", [2, 3, 4])
def test_showdown_board_and_reward_scaling(num_players: int):
    env = raw_env(num_players=num_players)
    env.reset(seed=42)

    while not any(env.terminations.values()):
        # OpenSpiel action 1 represents check when no bet is outstanding and
        # call otherwise, so an all-check/call trajectory reaches showdown.
        assert env.observe(env.agent_selection)["action_mask"][1] == 1
        env.step(1)

    state = json.loads(env.texas_holdem_env.game_state.to_json())
    assert len(state["board_cards"]) == 10  # five two-character cards
    assert state["betting_history"].count("/") == 3
    assert sum(env.rewards.values()) == pytest.approx(0.0)
    for agent_id, agent in enumerate(env.possible_agents):
        assert env.rewards[agent] == pytest.approx(
            env.texas_holdem_env.game_state.returns()[agent_id] * env.reward_scale
        )

    env.close()


@pytest.mark.parametrize("num_players", [2, 3, 4])
def test_raise_caps_and_maximum_contribution(num_players: int):
    env = raw_env(num_players=num_players)
    env.reset(seed=42)

    while not any(env.terminations.values()):
        action_mask = env.observe(env.agent_selection)["action_mask"]
        env.step(2 if action_mask[2] else 1)

    state = json.loads(env.texas_holdem_env.game_state.to_json())
    assert state["player_contributions"] == [48] * num_players
    assert state["betting_history"].split("/") == [
        "rrr" + "c" * (num_players - 1),
        "rrrr" + "c" * (num_players - 1),
        "rrrr" + "c" * (num_players - 1),
        "rrrr" + "c" * (num_players - 1),
    ]

    env.close()


@pytest.mark.parametrize("num_players", [2, 3, 4])
def test_random_legal_action_games(num_players: int):
    env = raw_env(num_players=num_players)
    action_rng = np.random.default_rng(1234)

    for seed in range(100):
        env.reset(seed=seed)
        while not any(env.terminations.values()):
            legal_actions = np.flatnonzero(
                env.observe(env.agent_selection)["action_mask"]
            )
            env.step(int(action_rng.choice(legal_actions)))

        raw_returns = env.texas_holdem_env.game_state.returns()
        assert sum(raw_returns) == pytest.approx(0.0)
        for agent_id, agent in enumerate(env.possible_agents):
            assert env.rewards[agent] == pytest.approx(
                raw_returns[agent_id] * env.reward_scale
            )

    env.close()


def test_registry_exposes_v5_as_latest():
    assert spec("aec", "classic/texas_holdem").version == 5
    registry_env = make("aec", "classic/texas_holdem-v5", num_players=3)
    registry_env.reset(seed=42)
    assert len(registry_env.possible_agents) == 3
    registry_env.close()


def test_rgb_array_rendering_uses_openspiel_state():
    env = raw_env(render_mode="rgb_array", screen_height=300)
    env.reset(seed=42)

    initial_frame = env.render()
    assert initial_frame.shape[0] == 300
    assert initial_frame.shape[2] == 3
    assert initial_frame.dtype == np.uint8

    for _ in range(4):
        env.step(1)
    later_frame = env.render()
    assert later_frame.shape == initial_frame.shape
    assert not np.array_equal(initial_frame, later_frame)

    env.close()
