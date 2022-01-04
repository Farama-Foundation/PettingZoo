import math
import warnings

import magent
import numpy as np
from gym.spaces import Box, Discrete
from gym.utils import EzPickle

from pettingzoo import AECEnv
from pettingzoo.magent.render import Renderer
from pettingzoo.utils import agent_selector, wrappers
from pettingzoo.utils.conversions import from_parallel_wrapper, parallel_wrapper_fn

from .battle_v3 import KILL_REWARD, get_config
from .magent_env import magent_parallel_env, make_env

"""
Same as [battle](./battle) but with fewer agents arrayed in a larger space with obstacles.

A small-scale team battle, where agents have to figure out the optimal way to coordinate their small team in a large space and maneuver around obstacles in order to defeat the opposing team. Agents are rewarded for their individual performance, and not for the performance of their neighbors, so coordination is difficult.  Agents slowly regain HP over time, so it is best to kill an opposing agent quickly. Specifically, agents have 10 HP, are damaged 2 HP by each attack, and recover 0.1 HP every turn.

Like all MAgent environments, agents can either move or attack each turn. An attack against another agent on their own team will not be registered.

### Arguments

:param map_size: Sets dimensions of the (square) map. Minimum size is 46.
:param minimap_mode: Turns on global minimap observations. These observations include your and your opponents piece densities binned over the 2d grid of the observation space. Also includes your `agent_position`, the absolute position on the map (rescaled from 0 to 1).
:param step_reward:  reward added unconditionally
:param dead_penalty:  reward added when killed
:param attack_penalty:  reward added for attacking
:param attack_opponent_reward:  Reward added for attacking an opponent
:param max_cycles:  number of frames (a step for each agent) until game terminates
:param extra_features: Adds additional features to observation (see table). Default False
"""

default_map_size = 80
max_cycles_default = 1000
minimap_mode_default = False
default_reward_args = dict(step_reward=-0.005, dead_penalty=-0.1, attack_penalty=-0.1, attack_opponent_reward=0.2)


def parallel_env(map_size=default_map_size, max_cycles=max_cycles_default, minimap_mode=minimap_mode_default, extra_features=False, **reward_args):
    env_reward_args = dict(**default_reward_args)
    env_reward_args.update(reward_args)
    return _parallel_env(map_size, minimap_mode, env_reward_args, max_cycles, extra_features)


def raw_env(map_size=default_map_size, max_cycles=max_cycles_default, minimap_mode=minimap_mode_default, extra_features=False, **reward_args):
    return from_parallel_wrapper(parallel_env(map_size, max_cycles, minimap_mode, extra_features, **reward_args))


env = make_env(raw_env)


class _parallel_env(magent_parallel_env, EzPickle):
    metadata = {'render.modes': ['human', 'rgb_array'], 'name': "battlefield_v3"}

    def __init__(self, map_size, minimap_mode, reward_args, max_cycles, extra_features):
        EzPickle.__init__(self, map_size, minimap_mode, reward_args, max_cycles, extra_features)
        assert map_size >= 46, "size of map must be at least 46"
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

        width = map_size
        height = map_size

        init_num = 20

        gap = 3
        leftID, rightID = 0, 1

        # left
        pos = []
        for y in range(10, 45):
            pos.append((width / 2 - 5, y))
            pos.append((width / 2 - 4, y))
        for y in range(50, height // 2 + 25):
            pos.append((width / 2 - 5, y))
            pos.append((width / 2 - 4, y))

        for y in range(height // 2 - 25, height - 50):
            pos.append((width / 2 + 5, y))
            pos.append((width / 2 + 4, y))
        for y in range(height - 45, height - 10):
            pos.append((width / 2 + 5, y))
            pos.append((width / 2 + 4, y))

        for x, y in pos:
            if not (0 < x < width - 1 and 0 < y < height - 1):
                assert False
        env.add_walls(pos=pos, method="custom")

        n = init_num
        side = int(math.sqrt(n)) * 2
        pos = []
        for x in range(width // 2 - gap - side, width // 2 - gap - side + side, 2):
            for y in range((height - side) // 2, (height - side) // 2 + side, 2):
                pos.append([x, y, 0])

        for x, y, _ in pos:
            if not (0 < x < width - 1 and 0 < y < height - 1):
                assert False
        env.add_agents(handles[leftID], method="custom", pos=pos)

        # right
        n = init_num
        side = int(math.sqrt(n)) * 2
        pos = []
        for x in range(width // 2 + gap, width // 2 + gap + side, 2):
            for y in range((height - side) // 2, (height - side) // 2 + side, 2):
                pos.append([x, y, 0])

        for x, y, _ in pos:
            if not (0 < x < width - 1 and 0 < y < height - 1):
                assert False
        env.add_agents(handles[rightID], method="custom", pos=pos)
