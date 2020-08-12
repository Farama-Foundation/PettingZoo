from .all_modules import *

import pytest
from .all_modules import all_environments
import pettingzoo.tests.api_test as api_test

from .error_tests import error_test
from .seed_test import seed_test, check_environment_deterministic
from .render_test import render_test



parameterized_envs = [
    # generic atari parameters
    (boxing_v0.env, dict(obs_type="grayscale_image")),
    (boxing_v0.env, dict(obs_type="ram")),
    (boxing_v0.env, dict(full_action_space=False)),

    (combat_plane_v0.env, dict(game_version="jet")),
    (combat_plane_v0.env, dict(guided_missile=True)),

    (combat_tank_v0.env, dict(has_maze=True)),
    (combat_tank_v0.env, dict(is_invisible=True)),
    (combat_tank_v0.env, dict(billiard_hit=True)),

    (maze_craze_v0.env, dict(game_version="race")),
    (maze_craze_v0.env, dict(game_version="capture")),
    (maze_craze_v0.env, dict(visibilty_level=1)),
    (maze_craze_v0.env, dict(visibilty_level=3)),

    (space_invaders_v0.env, dict(alternating_control=True,moving_shields=True,zigzaging_bombs=True,fast_bomb=True,invisible_invaders=True)),

    (knights_archers_zombies_v0.env, dict(spawn_rate=50)),
    (knights_archers_zombies_v0.env, dict(num_knights=4,num_archers=5)),
    (knights_archers_zombies_v0.env, dict(killable_knights=True, killable_archers=True)),
    (knights_archers_zombies_v0.env, dict(killable_knights=False, killable_archers=False)),
    (knights_archers_zombies_v0.env, dict(black_death=False)),
    (knights_archers_zombies_v0.env, dict(line_death=False)),
    (knights_archers_zombies_v0.env, dict(pad_observation=False)),
    (knights_archers_zombies_v0.env, dict(max_frames=100)),

    (pistonball_v0.env, dict(local_ratio=0.7)),
    (pistonball_v0.env, dict(continuous=True)),
    (pistonball_v0.env, dict(continuous=False)),
    (pistonball_v0.env, dict(random_drop=True, starting_angular_momentum=True)),
    (pistonball_v0.env, dict(random_drop=False, starting_angular_momentum=False)),

    (prison_v1.env, dict(continuous=True)),
    (prison_v1.env, dict(continuous=False)),
    (prison_v1.env, dict(vector_observation=True)),
    (prison_v1.env, dict(vector_observation=False)),
    (prison_v1.env, dict(num_floors=1)),
    (prison_v1.env, dict(num_floors=5)),
    (prison_v1.env, dict(synchronized_start=True)),
    (prison_v1.env, dict(synchronized_start=False)),
    (prison_v1.env, dict(identical_aliens=True)),
    (prison_v1.env, dict(identical_aliens=False)),
    (prison_v1.env, dict(random_aliens=True)),
    (prison_v1.env, dict(random_aliens=False)),

    (prospector_v0.env, dict(ind_reward=0.8, group_reward=0.1, other_group_reward=0.1,
    prospec_find_gold_reward=1, prospec_handoff_gold_reward=1, banker_receive_gold_reward=1,
    banker_deposit_gold_reward=1, max_frames=900)),

    (go_v0.env, dict(board_size = 13, komi = 2.5)),
    (go_v0.env, dict(board_size = 9, komi = 0.)),

    (hanabi_v0.env, dict(colors = 3)),
    (hanabi_v0.env, dict(ranks = 3)),
    (hanabi_v0.env, dict(players=4)),
    (hanabi_v0.env, dict(hand_size=5)),
    (hanabi_v0.env, dict(max_information_tokens=3)),
    (hanabi_v0.env, dict(max_life_tokens=2)),
    (hanabi_v0.env, dict(colors = 5, ranks = 3, players=4, hand_size=5, max_information_tokens=3, max_life_tokens=2)),
    (hanabi_v0.env, dict(observation_type=0)),
    (hanabi_v0.env, dict(observation_type=1)),
    (hanabi_v0.env, dict(random_start_player=False)),
    (hanabi_v0.env, dict(random_start_player=True)),
    
    (simple_adversary_v0.env, dict(N=4)),
    (simple_reference_v0.env, dict(local_ratio=0.2)),
    (simple_spread_v0.env, dict(N=5)),
    (simple_tag_v0.env, dict(num_good=5,num_adversaries=10,num_obstacles=4)),
    (simple_tag_v0.env, dict(num_good=1,num_adversaries=1,num_obstacles=1)),
    (simple_world_comm_v0.env, dict(num_good=5,num_adversaries=10,num_obstacles=4,num_food=3)),
    (simple_world_comm_v0.env, dict(num_good=1,num_adversaries=1,num_obstacles=1,num_food=1)),

    (multiwalker_v0.env, dict(n_walkers=10)),
    (multiwalker_v0.env, dict(reward_mech="global")),
    (multiwalker_v0.env, dict(terminate_on_fall=True)),
    (multiwalker_v0.env, dict(terminate_on_fall=False)),

    (pursuit_v0.env, dict(xs=8,ys=19)),
    (pursuit_v0.env, dict(reward_mech="local")),
    (pursuit_v0.env, dict(reward_mech="global")),
    (pursuit_v0.env, dict(n_evaders=5,n_pursuers=16)),
    (pursuit_v0.env, dict(obs_range=15)),
    (pursuit_v0.env, dict(n_catch=3)),
    (pursuit_v0.env, dict(random_opponents=True)),
    (pursuit_v0.env, dict(random_opponents=True, max_opponents=15)),
    (pursuit_v0.env, dict(freeze_evaders=True)),
    (pursuit_v0.env, dict(train_pursuit=True)),
    # what is up with the ally_layer and opponent_layer parameters?

    (waterworld_v0.env, dict(n_pursuers=3,n_evaders=6)),
    (waterworld_v0.env, dict(n_coop=1)),
    (waterworld_v0.env, dict(n_coop=1)),
    (waterworld_v0.env, dict(n_poison=4)),
    (waterworld_v0.env, dict(n_sensors=4)),
    (waterworld_v0.env, dict(terminate_on_fall=False)),
    (waterworld_v0.env, dict(reward_mech="global")),
    (waterworld_v0.env, dict(speed_features=False)),
]

@pytest.mark.parametrize(("env_constr", "kwargs"), parameterized_envs)
def test_module(env_constr, kwargs):
    _env = env_constr(**kwargs)
    print(kwargs)
    api_test.api_test(_env)

    # seed_test
    #seed_test(lambda seed=None: env_constr(seed=seed, **kwargs))

    # args are different test
    # SEED = 0x7267a520
    # if should_seed:
    #     assert not check_environment_deterministic(env_constr(seed=SEED, **kwargs), env_constr(seed=SEED))
    # else:
    #     assert not check_environment_deterministic(env_constr(**kwargs), env_constr())
