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
max_cycles_default = 1000
KILL_REWARD = 5
minimap_mode_default = False
default_reward_args = dict(step_reward=-0.005, dead_penalty=-0.1, attack_penalty=-0.1, attack_opponent_reward=0.2)


def parallel_env(map_size=default_map_size, max_cycles=max_cycles_default, minimap_mode=minimap_mode_default, extra_features=False, **reward_args):
    env_reward_args = dict(**default_reward_args)
    env_reward_args.update(reward_args)
    return _parallel_env(map_size, minimap_mode, env_reward_args, max_cycles, extra_features)


def raw_env(map_size=default_map_size, max_cycles=max_cycles_default, minimap_mode=minimap_mode_default, extra_features=False, **reward_args):
    return parallel_to_aec_wrapper(parallel_env(map_size, max_cycles, minimap_mode, extra_features, **reward_args))


env = make_env(raw_env)


def get_config(map_size, minimap_mode, step_reward, dead_penalty, attack_penalty, attack_opponent_reward):
    gw = magent.gridworld
    cfg = gw.Config()

    cfg.set({"map_width": map_size, "map_height": map_size})
    cfg.set({"minimap_mode": minimap_mode})
    cfg.set({"embedding_size": 10})

    options = {
        'width': 1, 'length': 1, 'hp': 10, 'speed': 2,
        'view_range': gw.CircleRange(6), 'attack_range': gw.CircleRange(1.5),
        'damage': 2, 'kill_reward': KILL_REWARD, 'step_recover': 0.1,
        'step_reward': step_reward, 'dead_penalty': dead_penalty, 'attack_penalty': attack_penalty
    }
    small = cfg.register_agent_type(
        "small",
        options
    )

    g0 = cfg.add_group(small)
    g1 = cfg.add_group(small)

    a = gw.AgentSymbol(g0, index='any')
    b = gw.AgentSymbol(g1, index='any')

    # reward shaping to encourage attack
    cfg.add_reward_rule(gw.Event(a, 'attack', b), receiver=a, value=attack_opponent_reward)
    cfg.add_reward_rule(gw.Event(b, 'attack', a), receiver=b, value=attack_opponent_reward)

    return cfg


class _parallel_env(magent_parallel_env, EzPickle):
    metadata = {
        "render.modes": ["human", "rgb_array"],
        'name': "battle_v3",
        "video.frames_per_second": 5,
        }

    def __init__(self, map_size, minimap_mode, reward_args, max_cycles, extra_features):
        EzPickle.__init__(self, map_size, minimap_mode, reward_args, max_cycles, extra_features)
        assert map_size >= 12, "size of map must be at least 12"
        env = magent.GridWorld(get_config(map_size, minimap_mode, **reward_args), map_size=map_size)
        self.leftID = 0
        self.rightID = 1
        reward_vals = np.array([KILL_REWARD] + list(reward_args.values()))
        reward_range = [np.minimum(reward_vals, 0).sum(), np.maximum(reward_vals, 0).sum()]
        names = ["red", "blue"]
        super().__init__(env, env.get_handles(), names, map_size, max_cycles, reward_range, minimap_mode, extra_features)

    def generate_map(self):
        env, map_size, handles = self.env, self.map_size, self.handles
        """ generate a map, which consists of two squares of agents"""
        width = height = map_size
        init_num = map_size * map_size * 0.04
        gap = 3

        self.leftID, self.rightID = self.rightID, self.leftID

        # left
        n = init_num
        side = int(math.sqrt(n)) * 2
        pos = []
        for x in range(width // 2 - gap - side, width // 2 - gap - side + side, 2):
            for y in range((height - side) // 2, (height - side) // 2 + side, 2):
                if 0 < x < width - 1 and 0 < y < height - 1:
                    pos.append([x, y, 0])
        team1_size = len(pos)
        env.add_agents(handles[self.leftID], method="custom", pos=pos)

        # right
        n = init_num
        side = int(math.sqrt(n)) * 2
        pos = []
        for x in range(width // 2 + gap, width // 2 + gap + side, 2):
            for y in range((height - side) // 2, (height - side) // 2 + side, 2):
                if 0 < x < width - 1 and 0 < y < height - 1:
                    pos.append([x, y, 0])

        pos = pos[:team1_size]
        env.add_agents(handles[self.rightID], method="custom", pos=pos)
