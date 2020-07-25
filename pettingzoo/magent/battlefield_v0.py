from gym.spaces import Discrete, Box
import numpy as np
import warnings
import magent
from pettingzoo import AECEnv
import math
from pettingzoo.magent.render import Renderer
from pettingzoo.utils import agent_selector, wrappers
from .magent_env import magent_parallel_env, make_env
from pettingzoo.utils._parallel_env import _parallel_env_wrapper
from .battle_v0 import get_config
from gym.utils import EzPickle


def raw_env(seed=None, max_frames=1000, **reward_args):
    map_size = 80
    return _parallel_env_wrapper(_parallel_env(map_size, reward_args, max_frames, seed))


env = make_env(raw_env)


class _parallel_env(magent_parallel_env, EzPickle):
    def __init__(self, map_size, reward_args, max_frames, seed):
        EzPickle.__init__(self, map_size, reward_args, max_frames, seed)
        env = magent.GridWorld(get_config(map_size, **reward_args), map_size=map_size)
        self.leftID = 0
        self.rightID = 1
        names = ["red", "blue"]
        super().__init__(env, env.get_handles(), names, map_size, max_frames, seed)

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
        env.add_walls(pos=pos, method="custom")

        n = init_num
        side = int(math.sqrt(n)) * 2
        pos = []
        for x in range(width // 2 - gap - side, width // 2 - gap - side + side, 2):
            for y in range((height - side) // 2, (height - side) // 2 + side, 2):
                pos.append([x, y, 0])
        env.add_agents(handles[leftID], method="custom", pos=pos)

        # right
        n = init_num
        side = int(math.sqrt(n)) * 2
        pos = []
        for x in range(width // 2 + gap, width // 2 + gap + side, 2):
            for y in range((height - side) // 2, (height - side) // 2 + side, 2):
                pos.append([x, y, 0])
        env.add_agents(handles[rightID], method="custom", pos=pos)
