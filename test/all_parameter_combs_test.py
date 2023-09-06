from __future__ import annotations

import pytest

from pettingzoo.atari import (
    basketball_pong_v3,
    boxing_v2,
    combat_plane_v2,
    combat_tank_v2,
    double_dunk_v3,
    entombed_competitive_v3,
    entombed_cooperative_v3,
    flag_capture_v2,
    foozpong_v3,
    ice_hockey_v2,
    joust_v3,
    mario_bros_v3,
    maze_craze_v3,
    othello_v3,
    pong_v3,
    quadrapong_v4,
    space_invaders_v2,
    space_war_v2,
    surround_v2,
    tennis_v3,
    video_checkers_v4,
    volleyball_pong_v3,
    warlords_v3,
    wizard_of_wor_v3,
)
from pettingzoo.butterfly import (
    cooperative_pong_v5,
    knights_archers_zombies_v10,
    pistonball_v6,
)
from pettingzoo.classic import (
    chess_v6,
    connect_four_v3,
    gin_rummy_v4,
    go_v5,
    hanabi_v5,
    leduc_holdem_v4,
    rps_v2,
    texas_holdem_no_limit_v6,
    texas_holdem_v4,
    tictactoe_v3,
)
from pettingzoo.mpe import (
    simple_adversary_v3,
    simple_crypto_v3,
    simple_push_v3,
    simple_reference_v3,
    simple_speaker_listener_v4,
    simple_spread_v3,
    simple_tag_v3,
    simple_v3,
    simple_world_comm_v3,
)
from pettingzoo.sisl import multiwalker_v9, pursuit_v4, waterworld_v4
from pettingzoo.test import max_cycles_test, parallel_api_test
from pettingzoo.test.api_test import api_test
from pettingzoo.test.render_test import render_test
from pettingzoo.test.seed_test import parallel_seed_test, seed_test
from pettingzoo.test.state_test import state_test

parameterized_envs = [
    ["atari/space_war_v2", space_war_v2, dict(max_cycles=50)],
    ["atari/quadrapong_v4", quadrapong_v4, dict(max_cycles=50)],
    ["atari/basketball_pong_v3", basketball_pong_v3, dict(max_cycles=50)],
    [
        "atari/basketball_pong_v3",
        basketball_pong_v3,
        dict(num_players=4, max_cycles=50),
    ],
    ["atari/wizard_of_wor_v3", wizard_of_wor_v3, dict(max_cycles=50)],
    ["atari/ice_hockey_v2", ice_hockey_v2, dict(max_cycles=50)],
    ["atari/pong_v3", pong_v3, dict(max_cycles=50)],
    ["atari/pong_v3", pong_v3, dict(num_players=4, max_cycles=50)],
    ["atari/surround_v2", surround_v2, dict(max_cycles=50)],
    ["atari/entombed_competitive_v3", entombed_competitive_v3, dict(max_cycles=50)],
    ["atari/flag_capture_v2", flag_capture_v2, dict(max_cycles=50)],
    ["atari/entombed_cooperative_v3", entombed_cooperative_v3, dict(max_cycles=50)],
    ["atari/tennis_v3", tennis_v3, dict(max_cycles=50)],
    ["atari/warlords_v3", warlords_v3, dict(max_cycles=50)],
    ["atari/mario_bros_v3", mario_bros_v3, dict(max_cycles=50)],
    ["atari/joust_v3", joust_v3, dict(max_cycles=50)],
    ["atari/foozpong_v3", foozpong_v3, dict(max_cycles=50)],
    ["atari/foozpong_v3", foozpong_v3, dict(num_players=4, max_cycles=50)],
    ["atari/video_checkers_v4", video_checkers_v4, dict(max_cycles=50)],
    ["atari/othello_v3", othello_v3, dict(max_cycles=50)],
    ["atari/double_dunk_v3", double_dunk_v3, dict(max_cycles=50)],
    ["atari/volleyball_pong_v3", volleyball_pong_v3, dict(max_cycles=50)],
    [
        "atari/volleyball_pong_v3",
        volleyball_pong_v3,
        dict(num_players=4, max_cycles=50),
    ],
    ["butterfly/cooperative_pong_v5", cooperative_pong_v5, dict(max_cycles=50)],
    [
        "butterfly/cooperative_pong_v5",
        cooperative_pong_v5,
        dict(bounce_randomness=True, max_cycles=50),
    ],
    ["classic/connect_four_v3", connect_four_v3, dict()],
    ["classic/rps_v2", rps_v2, dict()],
    ["classic/chess_v6", chess_v6, dict()],
    ["classic/tictactoe_v3", tictactoe_v3, dict()],
    ["classic/gin_rummy_v4", gin_rummy_v4, dict()],
    ["classic/gin_rummy_v4", gin_rummy_v4, dict(opponents_hand_visible=True)],
    ["mpe/simple_v3", simple_v3, dict(max_cycles=50)],
    ["mpe/simple_v3", simple_v3, dict(continuous_actions=True, max_cycles=50)],
    ["mpe/simple_push_v3", simple_push_v3, dict(max_cycles=50)],
    [
        "mpe/simple_push_v3",
        simple_push_v3,
        dict(continuous_actions=True, max_cycles=50),
    ],
    ["mpe/simple_crypto_v3", simple_crypto_v3, dict(max_cycles=50)],
    [
        "mpe/simple_crypto_v3",
        simple_crypto_v3,
        dict(continuous_actions=True, max_cycles=50),
    ],
    ["mpe/simple_speaker_listener_v4", simple_speaker_listener_v4, dict(max_cycles=50)],
    [
        "mpe/simple_speaker_listener_v4",
        simple_speaker_listener_v4,
        dict(continuous_actions=True, max_cycles=50),
    ],
    ["atari/boxing_v2", boxing_v2, dict(max_cycles=50)],
    ["atari/boxing_v2", boxing_v2, dict(obs_type="grayscale_image", max_cycles=50)],
    ["atari/boxing_v2", boxing_v2, dict(obs_type="ram", max_cycles=50)],
    ["atari/combat_plane_v2", combat_plane_v2, dict(game_version="jet", max_cycles=50)],
    [
        "atari/combat_plane_v2",
        combat_plane_v2,
        dict(guided_missile=True, max_cycles=50),
    ],
    ["atari/combat_tank_v2", combat_tank_v2, dict(has_maze=True, max_cycles=50)],
    ["atari/combat_tank_v2", combat_tank_v2, dict(is_invisible=True, max_cycles=50)],
    ["atari/combat_tank_v2", combat_tank_v2, dict(billiard_hit=True, max_cycles=50)],
    ["atari/maze_craze_v3", maze_craze_v3, dict(game_version="race", max_cycles=50)],
    ["atari/maze_craze_v3", maze_craze_v3, dict(game_version="capture", max_cycles=50)],
    ["atari/maze_craze_v3", maze_craze_v3, dict(visibilty_level=1, max_cycles=50)],
    ["atari/maze_craze_v3", maze_craze_v3, dict(visibilty_level=3, max_cycles=50)],
    [
        "atari/space_invaders_v2",
        space_invaders_v2,
        dict(
            alternating_control=True,
            moving_shields=True,
            zigzaging_bombs=True,
            fast_bomb=True,
            invisible_invaders=True,
            max_cycles=50,
        ),
    ],
    ["classic/leduc_holdem_v4", leduc_holdem_v4, dict()],
    ["classic/texas_holdem_v4", texas_holdem_v4, dict(num_players=3)],
    ["classic/texas_holdem_v4", texas_holdem_v4, dict(num_players=4)],
    ["classic/texas_holdem_no_limit_v6", texas_holdem_no_limit_v6, dict()],
    ["classic/texas_holdem_no_limit_v6", texas_holdem_no_limit_v6, dict(num_players=3)],
    ["classic/texas_holdem_no_limit_v6", texas_holdem_no_limit_v6, dict(num_players=4)],
    [
        "butterfly/knights_archers_zombies_v10",
        knights_archers_zombies_v10,
        dict(max_cycles=50),
    ],
    [
        "butterfly/knights_archers_zombies_v10",
        knights_archers_zombies_v10,
        dict(spawn_rate=50, max_cycles=50),
    ],
    [
        "butterfly/knights_archers_zombies_v10",
        knights_archers_zombies_v10,
        dict(num_knights=4, num_archers=5, max_cycles=50),
    ],
    [
        "butterfly/knights_archers_zombies_v10",
        knights_archers_zombies_v10,
        dict(killable_knights=False, killable_archers=False, max_cycles=50),
    ],
    [
        "butterfly/knights_archers_zombies_v10",
        knights_archers_zombies_v10,
        dict(sequence_space=True, use_typemasks=True, max_cycles=50),
    ],
    [
        "butterfly/knights_archers_zombies_v10",
        knights_archers_zombies_v10,
        dict(vector_state=False, max_cycles=50),
    ],
    [
        "butterfly/knights_archers_zombies_v10",
        knights_archers_zombies_v10,
        dict(vector_state=False, pad_observation=False, max_cycles=50),
    ],
    [
        "butterfly/knights_archers_zombies_v10",
        knights_archers_zombies_v10,
        dict(max_cycles=100),
    ],
    [
        "butterfly/knights_archers_zombies_v10",
        knights_archers_zombies_v10,
        dict(max_zombies=2, max_arrows=60, max_cycles=50),
    ],
    ["butterfly/pistonball_v6", pistonball_v6, dict(max_cycles=50)],
    ["butterfly/pistonball_v6", pistonball_v6, dict(n_pistons=30, max_cycles=50)],
    ["butterfly/pistonball_v6", pistonball_v6, dict(continuous=False, max_cycles=50)],
    [
        "butterfly/pistonball_v6",
        pistonball_v6,
        dict(random_drop=False, random_rotate=False, max_cycles=50),
    ],
    ["classic/go_v5", go_v5, dict(board_size=13, komi=2.5)],
    ["classic/go_v5", go_v5, dict(board_size=9, komi=0.0)],
    ["classic/hanabi_v5", hanabi_v5, dict()],
    ["classic/hanabi_v5", hanabi_v5, dict(colors=3)],
    ["classic/hanabi_v5", hanabi_v5, dict(ranks=3)],
    ["classic/hanabi_v5", hanabi_v5, dict(players=4)],
    ["classic/hanabi_v5", hanabi_v5, dict(max_information_tokens=3)],
    ["classic/hanabi_v5", hanabi_v5, dict(max_life_tokens=2)],
    [
        "classic/hanabi_v5",
        hanabi_v5,
        dict(
            colors=5,
            ranks=3,
            players=4,
            hand_size=5,
            max_information_tokens=3,
            max_life_tokens=2,
        ),
    ],
    ["classic/hanabi_v5", hanabi_v5, dict(observation_type="minimal")],
    ["classic/hanabi_v5", hanabi_v5, dict(observation_type="seer")],
    ["classic/hanabi_v5", hanabi_v5, dict(random_start_player=True)],
    ["mpe/simple_adversary_v3", simple_adversary_v3, dict(N=4, max_cycles=50)],
    [
        "mpe/simple_reference_v3",
        simple_reference_v3,
        dict(local_ratio=0.2, max_cycles=50),
    ],
    ["mpe/simple_spread_v3", simple_spread_v3, dict(N=5, max_cycles=50)],
    [
        "mpe/simple_tag_v3",
        simple_tag_v3,
        dict(num_good=5, num_adversaries=10, num_obstacles=4, max_cycles=50),
    ],
    [
        "mpe/simple_tag_v3",
        simple_tag_v3,
        dict(num_good=1, num_adversaries=1, num_obstacles=1, max_cycles=50),
    ],
    [
        "mpe/simple_tag_v3",
        simple_tag_v3,
        dict(
            num_good=5,
            num_adversaries=10,
            num_obstacles=4,
            continuous_actions=True,
            max_cycles=50,
        ),
    ],
    [
        "mpe/simple_tag_v3",
        simple_tag_v3,
        dict(
            num_good=1,
            num_adversaries=1,
            num_obstacles=1,
            continuous_actions=True,
            max_cycles=50,
        ),
    ],
    [
        "mpe/simple_world_comm_v3",
        simple_world_comm_v3,
        dict(
            num_good=5, num_adversaries=10, num_obstacles=4, num_food=3, max_cycles=50
        ),
    ],
    [
        "mpe/simple_world_comm_v3",
        simple_world_comm_v3,
        dict(num_good=1, num_adversaries=1, num_obstacles=1, num_food=1, max_cycles=50),
    ],
    [
        "mpe/simple_world_comm_v3",
        simple_world_comm_v3,
        dict(
            num_good=5,
            num_adversaries=10,
            num_obstacles=4,
            num_food=3,
            continuous_actions=True,
            max_cycles=50,
        ),
    ],
    [
        "mpe/simple_world_comm_v3",
        simple_world_comm_v3,
        dict(
            num_good=1,
            num_adversaries=1,
            num_obstacles=1,
            num_food=1,
            continuous_actions=True,
            max_cycles=50,
        ),
    ],
    [
        "mpe/simple_adversary_v3",
        simple_adversary_v3,
        dict(N=4, continuous_actions=True, max_cycles=50),
    ],
    [
        "mpe/simple_reference_v3",
        simple_reference_v3,
        dict(local_ratio=0.2, continuous_actions=True, max_cycles=50),
    ],
    [
        "mpe/simple_spread_v3",
        simple_spread_v3,
        dict(N=5, continuous_actions=True, max_cycles=50),
    ],
    ["sisl/multiwalker_v9", multiwalker_v9, dict(n_walkers=10, max_cycles=50)],
    ["sisl/multiwalker_v9", multiwalker_v9, dict(shared_reward=False, max_cycles=50)],
    [
        "sisl/multiwalker_v9",
        multiwalker_v9,
        dict(terminate_on_fall=False, max_cycles=50),
    ],
    [
        "sisl/multiwalker_v9",
        multiwalker_v9,
        dict(terminate_on_fall=False, remove_on_fall=False, max_cycles=50),
    ],
    ["sisl/pursuit_v4", pursuit_v4, dict(max_cycles=50)],
    ["sisl/pursuit_v4", pursuit_v4, dict(x_size=8, y_size=19, max_cycles=50)],
    ["sisl/pursuit_v4", pursuit_v4, dict(shared_reward=True, max_cycles=50)],
    ["sisl/pursuit_v4", pursuit_v4, dict(n_evaders=5, n_pursuers=16, max_cycles=50)],
    ["sisl/pursuit_v4", pursuit_v4, dict(obs_range=15, max_cycles=50)],
    ["sisl/pursuit_v4", pursuit_v4, dict(n_catch=3, max_cycles=50)],
    ["sisl/pursuit_v4", pursuit_v4, dict(freeze_evaders=True, max_cycles=50)],
    [
        "sisl/waterworld_v4",
        waterworld_v4,
        dict(n_pursuers=3, n_evaders=6, max_cycles=50),
    ],
    ["sisl/waterworld_v4", waterworld_v4, dict(n_coop=1, max_cycles=50)],
    ["sisl/waterworld_v4", waterworld_v4, dict(n_poisons=4, max_cycles=50)],
    ["sisl/waterworld_v4", waterworld_v4, dict(n_sensors=4, max_cycles=50)],
    ["sisl/waterworld_v4", waterworld_v4, dict(local_ratio=0.5, max_cycles=50)],
    ["sisl/waterworld_v4", waterworld_v4, dict(speed_features=False, max_cycles=50)],
]


@pytest.mark.parametrize(["name", "env_module", "kwargs"], parameterized_envs)
def test_module(name, env_module, kwargs):
    _env = env_module.env(**kwargs)
    api_test(_env)

    if "classic/" not in name:
        parallel_api_test(env_module.parallel_env())
        max_cycles_test(env_module)
        parallel_seed_test(lambda: env_module.parallel_env(**kwargs), 500)

    # some atari environments fail this test
    if "atari/" not in name:
        seed_test(lambda: env_module.env(**kwargs), 500)

    render_test(lambda render_mode: env_module.env(render_mode=render_mode, **kwargs))

    if ("butterfly/" in name) or ("mpe/" in name):
        state_test(env_module.env(), env_module.parallel_env())

    try:
        if hasattr(env_module, "parallel_env") and "rps" not in name:
            _env.state()
            par_env = env_module.parallel_env(**kwargs)
            state_test(_env, par_env)
    except NotImplementedError:
        # no issue if state is simply not implemented
        pass
