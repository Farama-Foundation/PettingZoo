import math
import warnings

import magent
import numpy as np
from gym.spaces import Box, Discrete
from gym.utils import EzPickle

from pettingzoo import AECEnv
from pettingzoo.magent.render import Renderer
from pettingzoo.utils import agent_selector
from pettingzoo.utils.conversions import parallel_to_aec_wrapper, parallel_wrapper_fn

from .magent_env import magent_parallel_env, make_env

default_map_size = 45
max_cycles_default = 500
minimap_mode_default = False
default_reward_args = dict(tag_penalty=-0.2)


def parallel_env(map_size=default_map_size, max_cycles=max_cycles_default, minimap_mode=minimap_mode_default, extra_features=False, **reward_args):
    env_reward_args = dict(**default_reward_args)
    env_reward_args.update(reward_args)
    return _parallel_env(map_size, minimap_mode, env_reward_args, max_cycles, extra_features)


def raw_env(map_size=default_map_size, max_cycles=max_cycles_default, minimap_mode=minimap_mode_default, extra_features=False, **reward_args):
    return parallel_to_aec_wrapper(parallel_env(map_size, max_cycles, minimap_mode, extra_features, **reward_args))


env = make_env(raw_env)


def get_config(map_size, minimap_mode, tag_penalty):
    gw = magent.gridworld
    cfg = gw.Config()

    cfg.set({"map_width": map_size, "map_height": map_size})
    cfg.set({"minimap_mode": minimap_mode})
    cfg.set({"embedding_size": 10})

    options = {
        'width': 2, 'length': 2, 'hp': 1, 'speed': 1,
        'view_range': gw.CircleRange(5), 'attack_range': gw.CircleRange(2),
        'attack_penalty': tag_penalty
    }
    predator = cfg.register_agent_type(
        "predator",
        options
    )

    options = {
        'width': 1, 'length': 1, 'hp': 1, 'speed': 1.5,
        'view_range': gw.CircleRange(4), 'attack_range': gw.CircleRange(0)
    }
    prey = cfg.register_agent_type(
        "prey",
        options
    )

    predator_group = cfg.add_group(predator)
    prey_group = cfg.add_group(prey)

    a = gw.AgentSymbol(predator_group, index='any')
    b = gw.AgentSymbol(prey_group, index='any')

    cfg.add_reward_rule(gw.Event(a, 'attack', b), receiver=[a, b], value=[1, -1])

    return cfg


class _parallel_env(magent_parallel_env, EzPickle):
    metadata = {
        "render.modes": ["human", "rgb_array"],
        'name': "adversarial_pursuit_v3",
        "video.frames_per_second": 5,
        }

    def __init__(self, map_size, minimap_mode, reward_args, max_cycles, extra_features):
        EzPickle.__init__(self, map_size, minimap_mode, reward_args, max_cycles, extra_features)
        assert map_size >= 7, "size of map must be at least 7"
        env = magent.GridWorld(get_config(map_size, minimap_mode, **reward_args), map_size=map_size)

        handles = env.get_handles()
        reward_vals = np.array([1, -1, -1, -1, -1] + list(reward_args.values()))
        reward_range = [np.minimum(reward_vals, 0).sum(), np.maximum(reward_vals, 0).sum()]
        names = ["predator", "prey"]
        super().__init__(env, handles, names, map_size, max_cycles, reward_range, minimap_mode, extra_features)

    def generate_map(self):
        env, map_size = self.env, self.map_size
        handles = env.get_handles()

        env.add_walls(method="random", n=map_size * map_size * 0.03)
        env.add_agents(handles[0], method="random", n=map_size * map_size * 0.0125)
        env.add_agents(handles[1], method="random", n=map_size * map_size * 0.025)
