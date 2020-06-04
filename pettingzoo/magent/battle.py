from gym.spaces import Discrete, Box
import numpy as np
import warnings
import magent
from pettingzoo import AECEnv
import math
from pettingzoo.magent.render import Renderer
from pettingzoo.utils import agent_selector
from .magent_env import markov_env
from .markov_env_wrapper import markov_env_wrapper

def env(map_size=45):
    return markov_env_wrapper(battle_markov_env(map_size))

class battle_markov_env(markov_env):
    def __init__(self, map_size):
        env = magent.GridWorld("battle",map_size=map_size)
        self.leftID = 0
        self.rightID = 1
        super().__init__(env,map_size)

    def generate_map(self):
        env, map_size, handles = self.env,self.map_size,self.handles
        """ generate a map, which consists of two squares of agents"""
        width = height = map_size
        init_num = map_size * map_size * 0.04
        gap = 3

        self.leftID, self.rightID = self.rightID, self.leftID

        # left
        n = init_num
        side = int(math.sqrt(n)) * 2
        pos = []
        for x in range(width//2 - gap - side, width//2 - gap - side + side, 2):
            for y in range((height - side)//2, (height - side)//2 + side, 2):
                pos.append([x, y, 0])
        env.add_agents(handles[self.leftID], method="custom", pos=pos)

        # right
        n = init_num
        side = int(math.sqrt(n)) * 2
        pos = []
        for x in range(width//2 + gap, width//2 + gap + side, 2):
            for y in range((height - side)//2, (height - side)//2 + side, 2):
                pos.append([x, y, 0])
        env.add_agents(handles[self.rightID], method="custom", pos=pos)
