from gym.spaces import Discrete, Box
import numpy as np
import warnings
import magent
from pettingzoo import AECEnv
import math
from pettingzoo.magent.render import Renderer
from pettingzoo.utils import agent_selector
from .magent_env import magent_parallel_env, make_env
from pettingzoo.utils._parallel_env import _parallel_env_wrapper


def raw_env(map_size=45, seed=None):
    return _parallel_env_wrapper(_parallel_env(map_size, seed))


env = make_env(raw_env)


def load_config(map_size):
    gw = magent.gridworld
    cfg = gw.Config()

    cfg.set({"map_width": map_size, "map_height": map_size})
    cfg.set({"minimap_mode": True})

    cfg.set({"embedding_size": 10})

    melee = cfg.register_agent_type(
        "melee",
        {'width': 1, 'length': 1, 'hp': 10, 'speed': 1,
         'view_range': gw.CircleRange(6), 'attack_range': gw.CircleRange(1),
         'damage': 2, 'step_recover': 0.1, 'attack_in_group': True,
         'step_reward': -0.01, 'kill_reward': 0, 'dead_penalty': -0.1, 'attack_penalty': -1,
         })

    ranged = cfg.register_agent_type(
        "ranged",
        {'width': 1, 'length': 1, 'hp': 3, 'speed': 2,
         'view_range': gw.CircleRange(6), 'attack_range': gw.CircleRange(2),
         'damage': 2, 'step_recover': 0.1, 'attack_in_group': True,
         'step_reward': -0.01, 'kill_reward': 0, 'dead_penalty': -0.1, 'attack_penalty': -1,
         })

    g0 = cfg.add_group(melee)
    g1 = cfg.add_group(ranged)
    g2 = cfg.add_group(melee)
    g3 = cfg.add_group(ranged)

    arm0_0 = gw.AgentSymbol(g0, index='any')
    arm0_1 = gw.AgentSymbol(g1, index='any')
    arm1_0 = gw.AgentSymbol(g2, index='any')
    arm1_1 = gw.AgentSymbol(g3, index='any')

    # reward shaping
    cfg.add_reward_rule(gw.Event(arm0_0, 'attack', arm1_0), receiver=arm0_0, value=2)
    cfg.add_reward_rule(gw.Event(arm0_0, 'attack', arm1_1), receiver=arm0_0, value=2)
    cfg.add_reward_rule(gw.Event(arm0_1, 'attack', arm1_0), receiver=arm0_1, value=2)
    cfg.add_reward_rule(gw.Event(arm0_1, 'attack', arm1_1), receiver=arm0_1, value=2)

    cfg.add_reward_rule(gw.Event(arm1_0, 'attack', arm0_0), receiver=arm1_0, value=2)
    cfg.add_reward_rule(gw.Event(arm1_0, 'attack', arm0_1), receiver=arm1_0, value=2)
    cfg.add_reward_rule(gw.Event(arm1_1, 'attack', arm0_0), receiver=arm1_1, value=2)
    cfg.add_reward_rule(gw.Event(arm1_1, 'attack', arm0_1), receiver=arm1_1, value=2)

    # kill reward
    cfg.add_reward_rule(gw.Event(arm0_0, 'kill', arm1_0), receiver=arm0_0, value=100)
    cfg.add_reward_rule(gw.Event(arm0_0, 'kill', arm1_1), receiver=arm0_0, value=100)
    cfg.add_reward_rule(gw.Event(arm0_1, 'kill', arm1_0), receiver=arm0_1, value=100)
    cfg.add_reward_rule(gw.Event(arm0_1, 'kill', arm1_1), receiver=arm0_1, value=100)

    cfg.add_reward_rule(gw.Event(arm1_0, 'kill', arm0_0), receiver=arm1_0, value=100)
    cfg.add_reward_rule(gw.Event(arm1_0, 'kill', arm0_1), receiver=arm1_0, value=100)
    cfg.add_reward_rule(gw.Event(arm1_1, 'kill', arm0_0), receiver=arm1_1, value=100)
    cfg.add_reward_rule(gw.Event(arm1_1, 'kill', arm0_1), receiver=arm1_1, value=100)

    return cfg


def generate_map(env, map_size, handles):
    width = map_size
    height = map_size

    init_num = map_size * map_size * 0.04

    gap = 3
    # left
    n = init_num
    side = int(math.sqrt(n)) * 2
    pos = [[], []]
    ct = 0
    for x in range(width // 2 - gap - side, width // 2 - gap - side + side, 2):
        for y in range((height - side) // 2, (height - side) // 2 + side, 2):
            pos[ct % 2].append([x, y])
        ct += 1
    env.add_agents(handles[0], method="custom", pos=pos[0])
    env.add_agents(handles[1], method="custom", pos=pos[1])

    # right
    n = init_num
    side = int(math.sqrt(n)) * 2
    pos = [[], []]
    ct = 0
    for x in range(width // 2 + gap, width // 2 + gap + side, 2):
        for y in range((height - side) // 2, (height - side) // 2 + side, 2):
            pos[ct % 2].append([x, y])
        ct += 1
    env.add_agents(handles[2], method="custom", pos=pos[0])
    env.add_agents(handles[3], method="custom", pos=pos[1])


class _parallel_env(magent_parallel_env):
    def __init__(self, map_size, seed):
        env = magent.GridWorld(load_config(map_size))
        names = ["redmelee", "redranged", "bluemele", "blueranged"]
        super().__init__(env, env.get_handles(), names, map_size, seed)

    def generate_map(self):
        generate_map(self.env, self.map_size, self.handles)
