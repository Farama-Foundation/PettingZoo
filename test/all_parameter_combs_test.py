import pytest

from pettingzoo.test.api_test import api_test
from pettingzoo.test.render_test import render_test
from pettingzoo.test.seed_test import seed_test
from pettingzoo.test.state_test import state_test

from .all_modules import *  # noqa: F403

parameterized_envs = [
    ["atari/boxing_v2", boxing_v2, dict(obs_type="grayscale_image")],
    ["atari/boxing_v2", boxing_v2, dict(obs_type="ram")],
    ["atari/boxing_v2", boxing_v2, dict(full_action_space=False)],
    ["atari/combat_plane_v2", combat_plane_v2, dict(game_version="jet")],
    ["atari/combat_plane_v2", combat_plane_v2, dict(guided_missile=True)],
    ["atari/combat_tank_v2", combat_tank_v2, dict(has_maze=True)],
    ["atari/combat_tank_v2", combat_tank_v2, dict(is_invisible=True)],
    ["atari/combat_tank_v2", combat_tank_v2, dict(billiard_hit=True)],
    ["atari/maze_craze_v3", maze_craze_v3, dict(game_version="race")],
    ["atari/maze_craze_v3", maze_craze_v3, dict(game_version="capture")],
    ["atari/maze_craze_v3", maze_craze_v3, dict(visibilty_level=1)],
    ["atari/maze_craze_v3", maze_craze_v3, dict(visibilty_level=3)],
    [
        "atari/space_invaders_v2",
        space_invaders_v2,
        dict(
            alternating_control=True,
            moving_shields=True,
            zigzaging_bombs=True,
            fast_bomb=True,
            invisible_invaders=True,
        ),
    ],
    ["classic/leduc_holdem_v4", leduc_holdem_v4, dict(num_players=2)],
    ["classic/leduc_holdem_v4", leduc_holdem_v4, dict(num_players=3)],
    ["classic/leduc_holdem_v4", leduc_holdem_v4, dict(num_players=4)],
    ["classic/texas_holdem_v4", texas_holdem_v4, dict(num_players=2)],
    ["classic/texas_holdem_v4", texas_holdem_v4, dict(num_players=3)],
    ["classic/texas_holdem_v4", texas_holdem_v4, dict(num_players=4)],
    ["classic/texas_holdem_no_limit_v6", texas_holdem_no_limit_v6, dict(num_players=2)],
    ["classic/texas_holdem_no_limit_v6", texas_holdem_no_limit_v6, dict(num_players=3)],
    ["classic/texas_holdem_no_limit_v6", texas_holdem_no_limit_v6, dict(num_players=4)],
    [
        "butterfly/knights_archers_zombies_v10",
        knights_archers_zombies_v10,
        dict(spawn_rate=50),
    ],
    [
        "butterfly/knights_archers_zombies_v10",
        knights_archers_zombies_v10,
        dict(num_knights=4, num_archers=5),
    ],
    [
        "butterfly/knights_archers_zombies_v10",
        knights_archers_zombies_v10,
        dict(killable_knights=True, killable_archers=True),
    ],
    [
        "butterfly/knights_archers_zombies_v10",
        knights_archers_zombies_v10,
        dict(killable_knights=False, killable_archers=False),
    ],
    [
        "butterfly/knights_archers_zombies_v10",
        knights_archers_zombies_v10,
        dict(line_death=False),
    ],
    [
        "butterfly/knights_archers_zombies_v10",
        knights_archers_zombies_v10,
        dict(vector_state=False),
    ],
    [
        "butterfly/knights_archers_zombies_v10",
        knights_archers_zombies_v10,
        dict(vector_state=False, pad_observation=False),
    ],
    [
        "butterfly/knights_archers_zombies_v10",
        knights_archers_zombies_v10,
        dict(max_cycles=100),
    ],
    [
        "butterfly/knights_archers_zombies_v10",
        knights_archers_zombies_v10,
        dict(use_typemasks=False),
    ],
    [
        "butterfly/knights_archers_zombies_v10",
        knights_archers_zombies_v10,
        dict(max_zombies=2, max_arrows=60),
    ],
    ["butterfly/pistonball_v6", pistonball_v6, dict(continuous=True)],
    ["butterfly/pistonball_v6", pistonball_v6, dict(n_pistons=30)],
    ["butterfly/pistonball_v6", pistonball_v6, dict(continuous=False)],
    [
        "butterfly/pistonball_v6",
        pistonball_v6,
        dict(random_drop=True, random_rotate=True),
    ],
    [
        "butterfly/pistonball_v6",
        pistonball_v6,
        dict(random_drop=False, random_rotate=False),
    ],
    ["classic/go_v5", go_v5, dict(board_size=13, komi=2.5)],
    ["classic/go_v5", go_v5, dict(board_size=9, komi=0.0)],
    ["classic/hanabi_v4", hanabi_v4, dict(colors=3)],
    ["classic/hanabi_v4", hanabi_v4, dict(ranks=3)],
    ["classic/hanabi_v4", hanabi_v4, dict(players=4)],
    ["classic/hanabi_v4", hanabi_v4, dict(hand_size=5)],
    ["classic/hanabi_v4", hanabi_v4, dict(max_information_tokens=3)],
    ["classic/hanabi_v4", hanabi_v4, dict(max_life_tokens=2)],
    [
        "classic/hanabi_v4",
        hanabi_v4,
        dict(
            colors=5,
            ranks=3,
            players=4,
            hand_size=5,
            max_information_tokens=3,
            max_life_tokens=2,
        ),
    ],
    ["classic/hanabi_v4", hanabi_v4, dict(observation_type=0)],
    ["classic/hanabi_v4", hanabi_v4, dict(observation_type=1)],
    ["classic/hanabi_v4", hanabi_v4, dict(random_start_player=False)],
    ["classic/hanabi_v4", hanabi_v4, dict(random_start_player=True)],
    ["mpe/simple_adversary_v2", simple_adversary_v2, dict(N=4)],
    ["mpe/simple_reference_v2", simple_reference_v2, dict(local_ratio=0.2)],
    ["mpe/simple_spread_v2", simple_spread_v2, dict(N=5)],
    [
        "mpe/simple_tag_v2",
        simple_tag_v2,
        dict(num_good=5, num_adversaries=10, num_obstacles=4),
    ],
    [
        "mpe/simple_tag_v2",
        simple_tag_v2,
        dict(num_good=1, num_adversaries=1, num_obstacles=1),
    ],
    [
        "mpe/simple_world_comm_v2",
        simple_world_comm_v2,
        dict(num_good=5, num_adversaries=10, num_obstacles=4, num_food=3),
    ],
    [
        "mpe/simple_world_comm_v2",
        simple_world_comm_v2,
        dict(num_good=1, num_adversaries=1, num_obstacles=1, num_food=1),
    ],
    [
        "mpe/simple_adversary_v2",
        simple_adversary_v2,
        dict(N=4, continuous_actions=True),
    ],
    [
        "mpe/simple_reference_v2",
        simple_reference_v2,
        dict(local_ratio=0.2, continuous_actions=True),
    ],
    ["mpe/simple_spread_v2", simple_spread_v2, dict(N=5, continuous_actions=True)],
    [
        "mpe/simple_tag_v2",
        simple_tag_v2,
        dict(num_good=5, num_adversaries=10, num_obstacles=4, continuous_actions=True),
    ],
    [
        "mpe/simple_tag_v2",
        simple_tag_v2,
        dict(num_good=1, num_adversaries=1, num_obstacles=1, continuous_actions=True),
    ],
    [
        "mpe/simple_world_comm_v2",
        simple_world_comm_v2,
        dict(
            num_good=5,
            num_adversaries=10,
            num_obstacles=4,
            num_food=3,
            continuous_actions=True,
        ),
    ],
    [
        "mpe/simple_world_comm_v2",
        simple_world_comm_v2,
        dict(
            num_good=1,
            num_adversaries=1,
            num_obstacles=1,
            num_food=1,
            continuous_actions=True,
        ),
    ],
    ["sisl/multiwalker_v9", multiwalker_v9, dict(n_walkers=10)],
    ["sisl/multiwalker_v9", multiwalker_v9, dict(shared_reward=False)],
    ["sisl/multiwalker_v9", multiwalker_v9, dict(terminate_on_fall=False)],
    [
        "sisl/multiwalker_v8",
        multiwalker_v9,
        dict(terminate_on_fall=False, remove_on_fall=False),
    ],
    ["sisl/pursuit_v4", pursuit_v4, dict(x_size=8, y_size=19)],
    ["sisl/pursuit_v4", pursuit_v4, dict(shared_reward=True)],
    ["sisl/pursuit_v4", pursuit_v4, dict(n_evaders=5, n_pursuers=16)],
    ["sisl/pursuit_v4", pursuit_v4, dict(obs_range=15)],
    ["sisl/pursuit_v4", pursuit_v4, dict(n_catch=3)],
    ["sisl/pursuit_v4", pursuit_v4, dict(freeze_evaders=True)],
    ["sisl/waterworld_v4", waterworld_v4, dict(n_pursuers=3, n_evaders=6)],
    ["sisl/waterworld_v4", waterworld_v4, dict(n_coop=1)],
    ["sisl/waterworld_v4", waterworld_v4, dict(n_coop=1)],
    ["sisl/waterworld_v4", waterworld_v4, dict(n_poisons=4)],
    ["sisl/waterworld_v4", waterworld_v4, dict(n_sensors=4)],
    ["sisl/waterworld_v4", waterworld_v4, dict(local_ratio=0.5)],
    ["sisl/waterworld_v4", waterworld_v4, dict(speed_features=False)],
]


@pytest.mark.parametrize(["name", "env_module", "kwargs"], parameterized_envs)
def test_module(name, env_module, kwargs):
    _env = env_module.env(**kwargs)
    api_test(_env)

    # some atari environments fail this test
    if "atari/" not in name:
        seed_test(lambda: env_module.env(**kwargs), 50)

    render_test(lambda render_mode: env_module.env(render_mode=render_mode, **kwargs))
    if hasattr(env_module, "parallel_env"):
        par_env = env_module.parallel_env(**kwargs)
    try:
        _env.state()
        state_test(_env, par_env)
    except NotImplementedError:
        # no issue if state is simply not implemented
        pass
