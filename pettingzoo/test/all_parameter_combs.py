from .all_modules import *  # noqa: F403

import pytest
from .all_modules import all_environments
from.api_test import api_test


parameterized_envs = [
    (boxing_v1.env, dict(obs_type="grayscale_image")),
    (boxing_v1.env, dict(obs_type="ram")),
    (boxing_v1.env, dict(full_action_space=False)),

    (combat_plane_v1.env, dict(game_version="jet")),
    (combat_plane_v1.env, dict(guided_missile=True)),

    (combat_tank_v1.env, dict(has_maze=True)),
    (combat_tank_v1.env, dict(is_invisible=True)),
    (combat_tank_v1.env, dict(billiard_hit=True)),

    (maze_craze_v2.env, dict(game_version="race")),
    (maze_craze_v2.env, dict(game_version="capture")),
    (maze_craze_v2.env, dict(visibilty_level=1)),
    (maze_craze_v2.env, dict(visibilty_level=3)),

    (space_invaders_v1.env, dict(alternating_control=True, moving_shields=True, zigzaging_bombs=True, fast_bomb=True, invisible_invaders=True)),

    (knights_archers_zombies_v7.env, dict(spawn_rate=50)),
    (knights_archers_zombies_v7.env, dict(num_knights=4, num_archers=5)),
    (knights_archers_zombies_v7.env, dict(killable_knights=True, killable_archers=True)),
    (knights_archers_zombies_v7.env, dict(killable_knights=False, killable_archers=False)),
    (knights_archers_zombies_v7.env, dict(line_death=False)),
    (knights_archers_zombies_v7.env, dict(pad_observation=False)),
    (knights_archers_zombies_v7.env, dict(max_cycles=100)),

    (pistonball_v4.env, dict(local_ratio=0.7)),
    (pistonball_v4.env, dict(continuous=True)),
    (pistonball_v4.env, dict(n_pistons=30)),
    (pistonball_v4.env, dict(continuous=False)),
    (pistonball_v4.env, dict(random_drop=True, random_rotate=True)),
    (pistonball_v4.env, dict(random_drop=False, random_rotate=False)),

    (prison_v3.env, dict(continuous=True)),
    (prison_v3.env, dict(continuous=False)),
    (prison_v3.env, dict(vector_observation=True)),
    (prison_v3.env, dict(vector_observation=False)),
    (prison_v3.env, dict(num_floors=1)),
    (prison_v3.env, dict(num_floors=5)),
    (prison_v3.env, dict(synchronized_start=True)),
    (prison_v3.env, dict(synchronized_start=False)),
    (prison_v3.env, dict(identical_aliens=True)),
    (prison_v3.env, dict(identical_aliens=False)),
    (prison_v3.env, dict(random_aliens=True)),
    (prison_v3.env, dict(random_aliens=False)),

    (prospector_v4.env, dict(ind_reward=0.8, group_reward=0.1, other_group_reward=0.1,
                             prospec_find_gold_reward=1, prospec_handoff_gold_reward=1, banker_receive_gold_reward=1,
                             banker_deposit_gold_reward=1, max_cycles=900)),

    (go_v3.env, dict(board_size=13, komi=2.5)),
    (go_v3.env, dict(board_size=9, komi=0.)),

    (hanabi_v4.env, dict(colors=3)),
    (hanabi_v4.env, dict(ranks=3)),
    (hanabi_v4.env, dict(players=4)),
    (hanabi_v4.env, dict(hand_size=5)),
    (hanabi_v4.env, dict(max_information_tokens=3)),
    (hanabi_v4.env, dict(max_life_tokens=2)),
    (hanabi_v4.env, dict(colors=5, ranks=3, players=4, hand_size=5, max_information_tokens=3, max_life_tokens=2)),
    (hanabi_v4.env, dict(observation_type=0)),
    (hanabi_v4.env, dict(observation_type=1)),
    (hanabi_v4.env, dict(random_start_player=False)),
    (hanabi_v4.env, dict(random_start_player=True)),

    # Commented out due to rare segfault
    (tiger_deer_v3.env, dict(minimap_mode=True)),
    (battle_v3.env, dict(minimap_mode=False)),
    (battlefield_v3.env, dict(minimap_mode=False, extra_features=False)),
    (battlefield_v3.env, dict(minimap_mode=False, extra_features=True)),
    (battlefield_v3.env, dict(minimap_mode=True, extra_features=False)),
    (battlefield_v3.env, dict(minimap_mode=True, extra_features=True)),
    (adversarial_pursuit_v2.env, dict(map_size=15)),
    (battle_v3.env, dict(map_size=15)),
    (battlefield_v3.env, dict(map_size=46)),
    (combined_arms_v4.env, dict(map_size=16)),
    (tiger_deer_v3.env, dict(map_size=15)),

    (simple_adversary_v2.env, dict(N=4)),
    (simple_reference_v2.env, dict(local_ratio=0.2)),
    (simple_spread_v2.env, dict(N=5)),
    (simple_tag_v2.env, dict(num_good=5, num_adversaries=10, num_obstacles=4)),
    (simple_tag_v2.env, dict(num_good=1, num_adversaries=1, num_obstacles=1)),
    (simple_world_comm_v2.env, dict(num_good=5, num_adversaries=10, num_obstacles=4, num_food=3)),
    (simple_world_comm_v2.env, dict(num_good=1, num_adversaries=1, num_obstacles=1, num_food=1)),

    (multiwalker_v7.env, dict(n_walkers=10)),
    (multiwalker_v7.env, dict(local_ratio=0.5)),
    (multiwalker_v7.env, dict(terminate_on_fall=False)),
    (multiwalker_v7.env, dict(terminate_on_fall=False, remove_on_fall=False)),

    (pursuit_v3.env, dict(x_size=8, y_size=19)),
    (pursuit_v3.env, dict(local_ratio=0.5)),
    (pursuit_v3.env, dict(n_evaders=5, n_pursuers=16)),
    (pursuit_v3.env, dict(obs_range=15)),
    (pursuit_v3.env, dict(n_catch=3)),
    (pursuit_v3.env, dict(freeze_evaders=True)),

    (waterworld_v3.env, dict(n_pursuers=3, n_evaders=6)),
    (waterworld_v3.env, dict(n_coop=1)),
    (waterworld_v3.env, dict(n_coop=1)),
    (waterworld_v3.env, dict(n_poison=4)),
    (waterworld_v3.env, dict(n_sensors=4)),
    (waterworld_v3.env, dict(terminate_on_fall=False)),
    (waterworld_v3.env, dict(local_ratio=0.5)),
    (waterworld_v3.env, dict(speed_features=False)),
]


@pytest.mark.parametrize(("env_constr", "kwargs"), parameterized_envs)
def test_module(env_constr, kwargs):
    _env = env_constr(**kwargs)
    print(kwargs)
    api_test(_env)
