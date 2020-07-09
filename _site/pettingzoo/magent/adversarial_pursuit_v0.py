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


def get_config(map_size):
    gw = magent.gridworld
    cfg = gw.Config()

    cfg.set({"map_width": map_size, "map_height": map_size})

    predator = cfg.register_agent_type(
        "predator",
        {
            'width': 2, 'length': 2, 'hp': 1, 'speed': 1,
            'view_range': gw.CircleRange(5), 'attack_range': gw.CircleRange(2),
            'attack_penalty': -0.2
        })

    prey = cfg.register_agent_type(
        "prey",
        {
            'width': 1, 'length': 1, 'hp': 1, 'speed': 1.5,
            'view_range': gw.CircleRange(4), 'attack_range': gw.CircleRange(0)
        })

    predator_group = cfg.add_group(predator)
    prey_group = cfg.add_group(prey)

    a = gw.AgentSymbol(predator_group, index='any')
    b = gw.AgentSymbol(prey_group, index='any')

    cfg.add_reward_rule(gw.Event(a, 'attack', b), receiver=[a, b], value=[1, -1])

    return cfg


class _parallel_env(magent_parallel_env):
    def __init__(self, map_size, seed):
        env = magent.GridWorld(get_config(map_size), map_size=map_size)

        handles = env.get_handles()

        names = ["predator", "prey"]
        super().__init__(env, handles, names, map_size, seed)

    def generate_map(self):
        env, map_size = self.env, self.map_size
        handles = env.get_handles()

        env.add_walls(method="random", n=map_size * map_size * 0.03)
        env.add_agents(handles[0], method="random", n=map_size * map_size * 0.0125)
        env.add_agents(handles[1], method="random", n=map_size * map_size * 0.025)
