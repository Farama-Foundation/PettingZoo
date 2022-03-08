from .all_modules import *  # noqa: F403

import pytest
from .all_modules import all_environments
from pettingzoo.test.api_test import api_test
from pettingzoo.test.seed_test import seed_test, check_environment_deterministic
from pettingzoo.test.parallel_test import parallel_api_test
from pettingzoo.test.max_cycles_test import max_cycles_test
from pettingzoo.test.state_test import state_test
from pettingzoo.test.render_test import render_test
from pettingzoo.utils import aec_to_parallel, parallel_to_aec


parameterized_envs = [
    (boxing_v1, dict(obs_type="grayscale_image")),
    (boxing_v1, dict(obs_type="ram")),
    (boxing_v1, dict(full_action_space=False)),

    (combat_plane_v1, dict(game_version="jet")),
    (combat_plane_v1, dict(guided_missile=True)),

    (combat_tank_v1, dict(has_maze=True)),
    (combat_tank_v1, dict(is_invisible=True)),
    (combat_tank_v1, dict(billiard_hit=True)),

    (maze_craze_v2, dict(game_version="race")),
    (maze_craze_v2, dict(game_version="capture")),
    (maze_craze_v2, dict(visibilty_level=1)),
    (maze_craze_v2, dict(visibilty_level=3)),

    (space_invaders_v1, dict(alternating_control=True, moving_shields=True, zigzaging_bombs=True, fast_bomb=True, invisible_invaders=True)),

    (leduc_holdem_v4, dict(num_players=2)),
    (leduc_holdem_v4, dict(num_players=3)),
    (leduc_holdem_v4, dict(num_players=4)),

    (texas_holdem_v4, dict(num_players=2)),
    (texas_holdem_v4, dict(num_players=3)),
    (texas_holdem_v4, dict(num_players=4)),

    (texas_holdem_no_limit_v6, dict(num_players=2)),
    (texas_holdem_no_limit_v6, dict(num_players=3)),
    (texas_holdem_no_limit_v6, dict(num_players=4)),

    (knights_archers_zombies_v9, dict(spawn_rate=50)),
    (knights_archers_zombies_v9, dict(num_knights=4, num_archers=5)),
    (knights_archers_zombies_v9, dict(killable_knights=True, killable_archers=True)),
    (knights_archers_zombies_v9, dict(killable_knights=False, killable_archers=False)),
    (knights_archers_zombies_v9, dict(line_death=False)),
    (knights_archers_zombies_v9, dict(pad_observation=False)),
    (knights_archers_zombies_v9, dict(max_cycles=100)),

    (pistonball_v6, dict(continuous=True)),
    (pistonball_v6, dict(n_pistons=30)),
    (pistonball_v6, dict(continuous=False)),
    (pistonball_v6, dict(random_drop=True, random_rotate=True)),
    (pistonball_v6, dict(random_drop=False, random_rotate=False)),

    (prison_v4, dict(continuous=True)),
    (prison_v4, dict(continuous=False)),
    (prison_v4, dict(vector_observation=True)),
    (prison_v4, dict(vector_observation=False)),
    (prison_v4, dict(num_floors=1)),
    (prison_v4, dict(num_floors=5)),
    (prison_v4, dict(synchronized_start=True)),
    (prison_v4, dict(synchronized_start=False)),
    (prison_v4, dict(identical_aliens=True)),
    (prison_v4, dict(identical_aliens=False)),
    (prison_v4, dict(random_aliens=True)),
    (prison_v4, dict(random_aliens=False)),

    (prospector_v4, dict(ind_reward=0.8, group_reward=0.1, other_group_reward=0.1,
                         prospec_find_gold_reward=1, prospec_handoff_gold_reward=1, banker_receive_gold_reward=1,
                         banker_deposit_gold_reward=1, max_cycles=900)),

    (go_v5, dict(board_size=13, komi=2.5)),
    (go_v5, dict(board_size=9, komi=0.)),

    (hanabi_v4, dict(colors=3)),
    (hanabi_v4, dict(ranks=3)),
    (hanabi_v4, dict(players=4)),
    (hanabi_v4, dict(hand_size=5)),
    (hanabi_v4, dict(max_information_tokens=3)),
    (hanabi_v4, dict(max_life_tokens=2)),
    (hanabi_v4, dict(colors=5, ranks=3, players=4, hand_size=5, max_information_tokens=3, max_life_tokens=2)),
    (hanabi_v4, dict(observation_type=0)),
    (hanabi_v4, dict(observation_type=1)),
    (hanabi_v4, dict(random_start_player=False)),
    (hanabi_v4, dict(random_start_player=True)),

    (tiger_deer_v3, dict(minimap_mode=True)),
    (battle_v3, dict(minimap_mode=False)),
    (battlefield_v4, dict(minimap_mode=False, extra_features=False)),
    (battlefield_v4, dict(minimap_mode=False, extra_features=True)),
    (battlefield_v4, dict(minimap_mode=True, extra_features=False)),
    (battlefield_v4, dict(minimap_mode=True, extra_features=True)),
    (adversarial_pursuit_v3, dict(map_size=15)),
    (battle_v3, dict(map_size=15)),
    (battlefield_v4, dict(map_size=46)),
    (combined_arms_v5, dict(map_size=16)),
    (tiger_deer_v3, dict(map_size=15)),

    (simple_adversary_v2, dict(N=4)),
    (simple_reference_v2, dict(local_ratio=0.2)),
    (simple_spread_v2, dict(N=5)),
    (simple_tag_v2, dict(num_good=5, num_adversaries=10, num_obstacles=4)),
    (simple_tag_v2, dict(num_good=1, num_adversaries=1, num_obstacles=1)),
    (simple_world_comm_v2, dict(num_good=5, num_adversaries=10, num_obstacles=4, num_food=3)),
    (simple_world_comm_v2, dict(num_good=1, num_adversaries=1, num_obstacles=1, num_food=1)),

    (simple_adversary_v2, dict(N=4, continuous_actions=True)),
    (simple_reference_v2, dict(local_ratio=0.2, continuous_actions=True)),
    (simple_spread_v2, dict(N=5, continuous_actions=True)),
    (simple_tag_v2, dict(num_good=5, num_adversaries=10, num_obstacles=4, continuous_actions=True)),
    (simple_tag_v2, dict(num_good=1, num_adversaries=1, num_obstacles=1, continuous_actions=True)),
    (simple_world_comm_v2, dict(num_good=5, num_adversaries=10, num_obstacles=4, num_food=3, continuous_actions=True)),
    (simple_world_comm_v2, dict(num_good=1, num_adversaries=1, num_obstacles=1, num_food=1, continuous_actions=True)),

    (multiwalker_v8, dict(n_walkers=10)),
    (multiwalker_v8, dict(shared_reward=False)),
    (multiwalker_v8, dict(terminate_on_fall=False)),
    (multiwalker_v8, dict(terminate_on_fall=False, remove_on_fall=False)),

    (pursuit_v4, dict(x_size=8, y_size=19)),
    (pursuit_v4, dict(shared_reward=True)),
    (pursuit_v4, dict(n_evaders=5, n_pursuers=16)),
    (pursuit_v4, dict(obs_range=15)),
    (pursuit_v4, dict(n_catch=3)),
    (pursuit_v4, dict(freeze_evaders=True)),

    (waterworld_v3, dict(n_pursuers=3, n_evaders=6)),
    (waterworld_v3, dict(n_coop=1)),
    (waterworld_v3, dict(n_coop=1)),
    (waterworld_v3, dict(n_poison=4)),
    (waterworld_v3, dict(n_sensors=4)),
    (waterworld_v3, dict(local_ratio=0.5)),
    (waterworld_v3, dict(speed_features=False)),
]


@pytest.mark.parametrize(("env_module", "kwargs"), parameterized_envs)
def test_module(env_module, kwargs):
    _env = env_module.env(**kwargs)
    api_test(_env)
    seed_test(lambda: env_module.env(**kwargs), 50)
    render_test(lambda: env_module.env(**kwargs))
    if hasattr(env_module, 'parallel_env'):
        par_env = env_module.parallel_env(**kwargs)
    try:
        _env.state()
        state_test(_env, par_env)
    except NotImplementedError:
        # no issue if state is simply not implemented
        pass
