import os
import json
from _docs_blurbs import all_docs

base_template = '''from ..base_atari_env import BaseAtariEnv, base_env_wrapper_fn


def raw_env(**kwargs):
    return BaseAtariEnv(game="{name}", num_players={num_players}, mode_num={mode}, **kwargs)


env = base_env_wrapper_fn(raw_env)
'''

doc_template = '''
### {env_pretty_name}

This environment is part of the [Atari environments](../atari.md). Please read that page first for general information.

| Observations | Actions | Agents  | Manual Control | Action Shape | Action Values | Observation Shape | Observation Values | Num States |
|--------------|---------|---------|----------------|--------------|---------------|-------------------|--------------------|------------|
| Graphical    | Discrete  | {num_players} | No      | (1,)    | [0,17]         | (210, 160, 3)         | (0,255)            | ?          |

`from pettingzoo.atari import {env_name}_v0`

`agents= {players}`

![{env_name} gif](../../gifs/atari_{env_name}.gif)

*AEC diagram*

{doc_blrb}

#### Environment parameters

Environment parameters are common to all Atari environments and are described in the [base Atari documentation](../atari.md) .

'''


envs = [
    {
        "fname": "boxing",
        "uname": "Boxing",
        "name": "boxing",
        "num_players": 2,
        "mode": None,
    },
    {
        "fname": "combat_tank",
        "uname": "Combat: Tank",
        "name": "combat",
        "num_players": 2,
        "mode": 4,
    },
    {
        "fname": "combat_tankpong",
        "uname": "Combat: Tank Pong",
        "name": "combat",
        "num_players": 2,
        "mode": 6,
    },
    {
        "fname": "combat_invisible_tank",
        "uname": "Combat: Invisible Tank",
        "name": "combat",
        "num_players": 2,
        "mode": 11,
    },
    {
        "fname": "combat_invisible_tankpong",
        "uname": "Combat: Invisible Tank Pong",
        "name": "combat",
        "num_players": 2,
        "mode": 14,
    },
    {
        "fname": "combat_biplane",
        "uname": "Combat: Biplane",
        "name": "combat",
        "num_players": 2,
        "mode": 16,
    },
    {
        "fname": "combat_jet",
        "uname": "Combat: Jet",
        "name": "combat",
        "num_players": 2,
        "mode": 21,
    },
    {
        "fname": "double_dunk",
        "uname": "Double Dunk",
        "name": "double_dunk",
        "num_players": 2,
        "mode": None,
    },
    {
        "fname": "entombed_competitive",
        "uname": "Entombed: Competitive",
        "name": "entombed",
        "num_players": 2,
        "mode": 2,
    },
    {
        "fname": "entombed_cooperative",
        "uname": "Entombed: Cooperative",
        "name": "entombed",
        "num_players": 2,
        "mode": 3,
    },
    {
        "fname": "flag_capture",
        "uname": "Flag Capture",
        "name": "flag_capture",
        "num_players": 2,
        "mode": None,
    },
    {
        "fname": "joust",
        "uname": "Joust",
        "name": "joust",
        "num_players": 2,
        "mode": None,
    },
    {
        "fname": "ice_hockey",
        "uname": "Ice Hockey",
        "name": "ice_hockey",
        "num_players": 2,
        "mode": None,
    },
    {
        "fname": "maze_craze_fully_seen",
        "uname": "Maze Craze: Full visibility",
        "name": "maze_craze",
        "num_players": 2,
        "mode": 0,
    },
    {
        "fname": "maze_craze_partial_vis",
        "uname": "Maze Craze: Partial visibility",
        "name": "maze_craze",
        "num_players": 2,
        "mode": (6-1)*4+3-1,
    },
    {
        "fname": "maze_craze_invisible",
        "uname": "Maze Craze: Invisible",
        "name": "maze_craze",
        "num_players": 2,
        "mode": (6-1)*4+4-1,
    },
    {
        "fname": "maze_craze_robbers",
        "uname": "Maze Craze: Robbers",
        "name": "maze_craze",
        "num_players": 2,
        "mode": (3-1)*4+1-1,
    },
    {
        "fname": "maze_craze_capture",
        "uname": "Maze Craze: Capture",
        "name": "maze_craze",
        "num_players": 2,
        "mode": (4-1)*4+1-1,
    },
    {
        "fname": "maze_craze_blockade",
        "uname": "Maze Craze: Blockade",
        "name": "maze_craze",
        "num_players": 2,
        "mode": (11-1)*4+1-1,
    },
    {
        "fname": "mario_bros",
        "uname": "Mario Bros",
        "name": "mario_bros",
        "num_players": 2,
        "mode": None,
    },
    {
        "fname": "othello",
        "uname": "Othello",
        "name": "othello",
        "num_players": 2,
        "mode": None,
    },
    {
        "fname": "pong",
        "uname": "Pong: Original",
        "name": "pong",
        "num_players": 2,
        "mode": None,
    },
    {
        "fname": "pong_basketball",
        "uname": "Pong: Basketball",
        "name": "pong",
        "num_players": 2,
        "mode": 44,
    },
    {
        "fname": "space_invaders_easy",
        "uname": "Space Invaders: Easy",
        "name": "space_invaders",
        "num_players": 2,
        "mode": 33,
    },
    {
        "fname": "space_invaders_difficult",
        "uname": "Space Invaders: Difficult",
        "name": "space_invaders",
        "num_players": 2,
        "mode": 44,
    },
    {
        "fname": "space_invaders_alternating",
        "uname": "Space Invaders: Alternating",
        "name": "space_invaders",
        "num_players": 2,
        "mode": 50,
    },
    {
        "fname": "surround",
        "uname": "Surround: Original",
        "name": "surround",
        "num_players": 2,
        "mode": None,
    },
    {
        "fname": "surround_erase",
        "uname": "Surround: Erase",
        "name": "surround",
        "num_players": 2,
        "mode": 7,
    },
    {
        "fname": "tennis",
        "uname": "Tennis",
        "name": "tennis",
        "num_players": 2,
        "mode": None,
    },
    {
        "fname": "video_checkers",
        "uname": "Video Checkers",
        "name": "video_checkers",
        "num_players": 2,
        "mode": None,
    },
    {
        "fname": "wizard_of_wor",
        "uname": "Wizard of Wor",
        "name": "wizard_of_wor",
        "num_players": 2,
        "mode": None,
    },
    {
        "fname": "warlords",
        "uname": "Warlords",
        "name": "warlords",
        "num_players": 4,
        "mode": None,
    },
    {
        "fname": "pong_four_player",
        "uname": "Pong: Doubles",
        "name": "pong",
        "num_players": 4,
        "mode": 5,
    },
    {
        "fname": "pong_quadrapong",
        "uname": "Pong: Quadrapong",
        "name": "pong",
        "num_players": 4,
        "mode": 33,
    },
    {
        "fname": "pong_volleyball",
        "uname": "Pong: Team Volleyball",
        "name": "pong",
        "num_players": 4,
        "mode": 41,
    },
]



def gen_games():
    os.mkdir("ale_games")
    for env in envs:
        name = f"ale_games/{env['fname']}.py"
        with open(name,'w') as file:
            file.write(base_template.format(**env))

def gen_imports():
    init_template = "from .games import {fname} as {fname}_v0\n"
    with open("atari_init.py",'w') as file:
        for env in envs:
            fname = env['fname']
            file.write(init_template.format(fname=fname))

def gen_ci_test_data():
    testsh_template = "python3 -m pettingzoo.tests.ci_test atari/{} $render $manual_control $bombardment $performance $save_obs\n"
    with open("atari_testsh.sh",'w') as file:
        for env in envs:
            file.write(testsh_template.format(env['fname']))

def gen_testsh_data():
    module_dict = {"atari/"+env['fname']: env['fname']+"_v0" for env in envs}

    testsh_template = '    "atari/{fname}": {fname}_v0,\n'
    with open("atari_mod.py",'w') as file:
        for env in envs:
            file.write(testsh_template.format(fname=env['fname']))

def gen_doc_data():
    player_names = ["first", "second", "third", "fourth"]
    os.mkdir("ale_docs")
    for env in envs:
        name = env['fname']
        doc_conent = all_docs[name] if name in all_docs else "*BLRB NEEDED!!!*\n"
        doc = doc_template.format(
            env_name=name,
            doc_blrb=doc_conent,
            num_players=env['num_players'],
            players=json.dumps([f"{player_names[i]}_0" for i in range(env['num_players'])]),
            env_pretty_name=env['uname'],
        )
        doc_path = f"ale_docs/{name}.md"
        with open(doc_path,'w') as file:
            file.write(doc)

def gen_doc_table():
    header = "| Environment | Observations | Actions | Agents  | Manual Control | Action Shape | Action Values | Observation Shape | Observation Values | Num States |"
    seperator = "|--------------|--------------|---------|---------|----------------|--------------|---------------|-------------------|--------------------|------------|"
    content_templ = "| [{uname}](atari/{env_name}.md)   | Graphical    | Discrete  | {num_players} | No      | (1,)    | [0,17]         | (210, 160, 3)         | (0,255)            | ?          |"

    content_list = [header,seperator]
    for env in envs:
        #name = env['fname']
        contents = content_templ.format(
            uname=env['uname'],
            env_name=env['fname'],
            num_players=env['num_players']
        )
        content_list.append(contents)

    with open("atari_doc.md",'w') as file:
        file.write("\n".join(content_list)+"\n")

gen_doc_data()
gen_doc_table()
