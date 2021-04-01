from pettingzoo import AECEnv
from gym import spaces
import rlcard
import random
import numpy as np
from pettingzoo.utils import wrappers
from .rlcard_base import RLCardBase


def env(**kwargs):
    env = raw_env(**kwargs)
    env = wrappers.CaptureStdoutWrapper(env)
    env = wrappers.TerminateIllegalWrapper(env, illegal_reward=-1)
    env = wrappers.AssertOutOfBoundsWrapper(env)
    env = wrappers.OrderEnforcingWrapper(env)
    return env


class raw_env(RLCardBase):

    metadata = {'render.modes': ['human'], "name": "mahjong_v3"}

    def __init__(self):
        super().__init__("mahjong", 4, (6, 34, 4))

    def render(self, mode='human'):
        for player in self.possible_agents:
            state = self.env.game.get_state(self._name_to_int(player))
            print("\n======== {}'s Hand ========".format(player))
            print(', '.join([c.get_str() for c in state['current_hand']]))
            print("\n{}'s Piles: ".format(player), ', '.join([c.get_str() for pile in state['players_pile'][self._name_to_int(player)] for c in pile]))
        print("\n======== Tiles on Table ========")
        print(', '.join([c.get_str() for c in state['table']]))
        print('\n')
