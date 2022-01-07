import random

import numpy as np
import rlcard
from gym import spaces
from rlcard.utils.utils import print_card

from pettingzoo import AECEnv
from pettingzoo.utils import wrappers
from pettingzoo.utils.agent_selector import agent_selector

from .rlcard_base import RLCardBase

"""
Leduc Hold'em is a variation of Limit Texas Hold'em with 2 players, 2 rounds and a deck of six cards (Jack, Queen, and King in 2 suits). At the beginning of the game, each player receives one card and, after betting, one public card is revealed. Another round follow. At the end, the player with the best hand wins and receives a reward (+1) and the loser receives -1. At any time, any player can fold.   

Our implementation wraps [RLCard](http://rlcard.org/games.html#leduc-hold-em) and you can refer to its documentation for additional details. Please cite their work if you use this game in research.

### Observation Space

The observation is a dictionary which contains an `'obs'` element which is the usual RL observation described below, and an  `'action_mask'` which holds the legal moves, described in the Legal Actions Mask section.

As described by [RLCard](https://github.com/datamllab/rlcard/blob/master/docs/games#leduc-holdem), the first 3 entries of the main observation space correspond to the player's hand (J, Q, and K) and the next 3 represent the public cards. Indexes 6 to 19 and 20 to 33 encode the number of chips by the current player and the opponent, respectively.

### Arguments

:param num_players: Sets the number of players in the game. Minimum is 2.
"""

def env(**kwargs):
    env = raw_env(**kwargs)
    env = wrappers.CaptureStdoutWrapper(env)
    env = wrappers.TerminateIllegalWrapper(env, illegal_reward=-1)
    env = wrappers.AssertOutOfBoundsWrapper(env)
    env = wrappers.OrderEnforcingWrapper(env)
    return env


class raw_env(RLCardBase):

    metadata = {'render.modes': ['human'], "name": "leduc_holdem_v4"}

    def __init__(self, num_players=2):
        super().__init__("leduc-holdem", num_players, (36,))

    def render(self, mode='human'):
        for player in self.possible_agents:
            state = self.env.game.get_state(self._name_to_int(player))
            print(f"\n=============== {player}'s Hand ===============")
            print_card(state['hand'])
            print("\n{}'s Chips: {}".format(player, state['my_chips']))
        print('\n================= Public Cards =================')
        print_card(state['public_card']) if state['public_card'] is not None else print('No public cards.')
        print('\n')
