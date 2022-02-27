import random

import numpy as np
import rlcard
from gym import spaces

from pettingzoo import AECEnv
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

    metadata = {
        "render.modes": ["human"],
        "name": "mahjong_v4",
        "is_parallelizable": False,
        "video.frames_per_second": 1,
    }

    def __init__(self):
        super().__init__("mahjong", 4, (6, 34, 4))

    def render(self, mode='human'):
        for player in self.possible_agents:
            state = self.env.game.get_state(self._name_to_int(player))
            print(f"\n======== {player}'s Hand ========")
            print(', '.join([c.get_str() for c in state['current_hand']]))
            print(f"\n{player}'s Piles: ", ', '.join([c.get_str() for pile in state['players_pile'][self._name_to_int(player)] for c in pile]))
        print("\n======== Tiles on Table ========")
        print(', '.join([c.get_str() for c in state['table']]))
        print('\n')
