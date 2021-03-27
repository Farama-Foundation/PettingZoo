from gym.spaces import Discrete, Box
import numpy as np
import warnings
import magent
from pettingzoo import AECEnv
import math
from pettingzoo.magent.render import Renderer
from pettingzoo.utils import agent_selector
from .magent_env import magent_parallel_env, make_env
from pettingzoo.utils.conversions import from_parallel_wrapper
from pettingzoo.utils.conversions import parallel_wrapper_fn
from gym.utils import EzPickle


default_map_size = 45
max_cycles_default = 300
minimap_mode_default = False
default_env_args = dict(tiger_step_recover=-0.1, deer_attacked=-0.1)


def parallel_env(map_size=default_map_size, max_cycles=max_cycles_default, minimap_mode=minimap_mode_default, extra_features=False, **env_args):
    env_env_args = dict(**default_env_args)
    env_env_args.update(env_args)
    return _parallel_env(map_size, minimap_mode, env_env_args, max_cycles, extra_features)


def raw_env(map_size=default_map_size, max_cycles=max_cycles_default, minimap_mode=minimap_mode_default, extra_features=False, **env_args):
    return from_parallel_wrapper(parallel_env(map_size, max_cycles, minimap_mode, extra_features, **env_args))


env = make_env(raw_env)


def get_config(map_size, minimap_mode, tiger_step_recover, deer_attacked):
    gw = magent.gridworld
    cfg = gw.Config()

    cfg.set({"map_width": map_size, "map_height": map_size})
    cfg.set({"embedding_size": 10})
    cfg.set({"minimap_mode": minimap_mode})

    options = {
        'width': 1, 'length': 1, 'hp': 5, 'speed': 1,
        'view_range': gw.CircleRange(1), 'attack_range': gw.CircleRange(0),
        'step_recover': 0.2,
        'kill_supply': 8, 'dead_penalty': -1.,
    }

    deer = cfg.register_agent_type(
        "deer",
        options)

    options = {
        'width': 1, 'length': 1, 'hp': 10, 'speed': 1,
        'view_range': gw.CircleRange(4), 'attack_range': gw.CircleRange(1),
        'damage': 1, 'step_recover': tiger_step_recover
    }
    tiger = cfg.register_agent_type(
        "tiger",
        options)

    deer_group = cfg.add_group(deer)
    tiger_group = cfg.add_group(tiger)

    a = gw.AgentSymbol(tiger_group, index='any')
    b = gw.AgentSymbol(tiger_group, index='any')
    c = gw.AgentSymbol(deer_group, index='any')

    # tigers get reward when they attack a deer simultaneously
    e1 = gw.Event(a, 'attack', c)
    e2 = gw.Event(b, 'attack', c)
    tiger_attack_rew = 1
    # reward is halved because the reward is double counted
    cfg.add_reward_rule(e1 & e2, receiver=[a, b], value=[tiger_attack_rew / 2, tiger_attack_rew / 2])
    cfg.add_reward_rule(e1, receiver=[c], value=[deer_attacked])

    return cfg


class _parallel_env(magent_parallel_env, EzPickle):
    metadata = {'render.modes': ['human', 'rgb_array'], 'name': "tiger_deer_v3"}

    def __init__(self, map_size, minimap_mode, reward_args, max_cycles, extra_features):
        EzPickle.__init__(self, map_size, minimap_mode, reward_args, max_cycles, extra_features)
        assert map_size >= 10, "size of map must be at least 10"
        env = magent.GridWorld(get_config(map_size, minimap_mode, **reward_args), map_size=map_size)

        handles = env.get_handles()
        reward_vals = np.array([1, -1] + list(reward_args.values()))
        reward_range = [np.minimum(reward_vals, 0).sum(), np.maximum(reward_vals, 0).sum()]

        names = ["deer", "tiger"]
        super().__init__(env, handles, names, map_size, max_cycles, reward_range, minimap_mode, extra_features)

    def generate_map(self):
        env, map_size = self.env, self.map_size
        handles = env.get_handles()

        env.add_walls(method="random", n=map_size * map_size * 0.04)
        env.add_agents(handles[0], method="random", n=map_size * map_size * 0.05)
        env.add_agents(handles[1], method="random", n=map_size * map_size * 0.01)
