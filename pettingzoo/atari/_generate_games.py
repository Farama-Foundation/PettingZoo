import os
import json

base_template = '''from ..base_atari_env import BaseAtariEnv, base_env_wrapper_fn


def raw_env(**kwargs):
    return BaseAtariEnv(game="{name}", num_players={num_players}, mode_num={mode}, **kwargs)


env = base_env_wrapper_fn(raw_env)
'''

envs = [
    {
        "fname": "backgammon",
        "name": "backgammon",
        "num_players": 2,
        "mode": None,
    },
    {
        "fname": "boxing",
        "name": "boxing",
        "num_players": 2,
        "mode": None,
    },
    {
        "fname": "combat_tank",
        "name": "combat",
        "num_players": 2,
        "mode": 4,
    },
    {
        "fname": "combat_tankpong",
        "name": "combat",
        "num_players": 2,
        "mode": 6,
    },
    {
        "fname": "combat_invisible_tank",
        "name": "combat",
        "num_players": 2,
        "mode": 11,
    },
    {
        "fname": "combat_invisible_tankpong",
        "name": "combat",
        "num_players": 2,
        "mode": 14,
    },
    {
        "fname": "combat_biplane",
        "name": "combat",
        "num_players": 2,
        "mode": 16,
    },
    {
        "fname": "combat_jet",
        "name": "combat",
        "num_players": 2,
        "mode": 21,
    },
    {
        "fname": "double_dunk",
        "name": "double_dunk",
        "num_players": 2,
        "mode": None,
    },
    {
        "fname": "entombed",
        "name": "entombed",
        "num_players": 2,
        "mode": None,
    },
    {
        "fname": "flag_capture",
        "name": "flag_capture",
        "num_players": 2,
        "mode": None,
    },
    {
        "fname": "joust",
        "name": "joust",
        "num_players": 2,
        "mode": None,
    },
    {
        "fname": "ice_hockey",
        "name": "ice_hockey",
        "num_players": 2,
        "mode": None,
    },
    {
        "fname": "maze_craze_fully_seen",
        "name": "maze_craze",
        "num_players": 2,
        "mode": 0,
    },
    {
        "fname": "maze_craze_partial_vis",
        "name": "maze_craze",
        "num_players": 2,
        "mode": (6_1)*4+3_1,
    },
    {
        "fname": "maze_craze_invisible",
        "name": "maze_craze",
        "num_players": 2,
        "mode": (6_1)*4+4_1,
    },
    {
        "fname": "maze_craze_robbers",
        "name": "maze_craze",
        "num_players": 2,
        "mode": (3_1)*4+1_1,
    },
    {
        "fname": "maze_craze_capture",
        "name": "maze_craze",
        "num_players": 2,
        "mode": (4_1)*4+1_1,
    },
    {
        "fname": "maze_craze_blockade",
        "name": "maze_craze",
        "num_players": 2,
        "mode": (11_1)*4+1_1,
    },
    {
        "fname": "mario_bros",
        "name": "mario_bros",
        "num_players": 2,
        "mode": None,
    },
    {
        "fname": "othello",
        "name": "othello",
        "num_players": 2,
        "mode": None,
    },
    {
        "fname": "pong",
        "name": "pong",
        "num_players": 2,
        "mode": None,
    },
    {
        "fname": "pong_basketball",
        "name": "pong",
        "num_players": 2,
        "mode": 44,
    },
    {
        "fname": "space_invaders_easy",
        "name": "space_invaders",
        "num_players": 2,
        "mode": 33,
    },
    {
        "fname": "space_invaders_difficult",
        "name": "space_invaders",
        "num_players": 2,
        "mode": 44,
    },
    {
        "fname": "space_invaders_alternating",
        "name": "space_invaders",
        "num_players": 2,
        "mode": 50,
    },
    {
        "fname": "surround",
        "name": "surround",
        "num_players": 2,
        "mode": None,
    },
    {
        "fname": "surround_erase",
        "name": "surround",
        "num_players": 2,
        "mode": 7,
    },
    {
        "fname": "tennis",
        "name": "tennis",
        "num_players": 2,
        "mode": None,
    },
    {
        "fname": "video_checkers",
        "name": "video_checkers",
        "num_players": 2,
        "mode": None,
    },
    {
        "fname": "wizard_of_wor",
        "name": "wizard_of_wor",
        "num_players": 2,
        "mode": None,
    },
    {
        "fname": "warlords_two_player",
        "name": "warlords",
        "num_players": 2,
        "mode": None,
    },
    {
        "fname": "warlords",
        "name": "warlords",
        "num_players": 4,
        "mode": None,
    },
    {
        "fname": "pong_four_player",
        "name": "pong",
        "num_players": 4,
        "mode": 5,
    },
    {
        "fname": "pong_quadrapong",
        "name": "pong",
        "num_players": 4,
        "mode": 33,
    },
    {
        "fname": "pong_volleyball",
        "name": "pong",
        "num_players": 4,
        "mode": 41,
    },
]
os.mkdir("ale_games")
for env in envs:
    name = f"ale_games/{env['fname']}.py"
    with open(name,'w') as file:
        file.write(base_template.format(**env))

init_template = "from .games import {fname} as {fname}_v0\n"
with open("atari_init.py",'w') as file:
    for env in envs:
        fname = env['fname']
        file.write(init_template.format(fname=fname))

testsh_template = "python3 -m pettingzoo.tests.ci_test atari/{} $render $manual_control $bombardment $performance $save_obs\n"
with open("atari_testsh.sh",'w') as file:
    for env in envs:
        file.write(testsh_template.format(env['fname']))

module_dict = {"atari/"+env['fname']: env['fname']+"_v0" for env in envs}

testsh_template = '    "atari/{fname}": {fname}_v0,\n'
with open("atari_mod.py",'w') as file:
    for env in envs:
        file.write(testsh_template.format(fname=env['fname']))
