import random

import numpy as np
import rlcard
from gym import spaces
from rlcard.games.uno.card import UnoCard

from pettingzoo import AECEnv
from pettingzoo.utils import wrappers
from pettingzoo.utils.agent_selector import agent_selector

from .rlcard_base import RLCardBase

"""
Uno is shedding game involving 2 players. At the beginning, each player receives 7 cards and the winner is the first player with no cards left. In order to discard a card from their hand, a player must match either the color or number of the card on top of the discard pile. If the player does not have a card to discard, then they will take a card from the draw pile. The deck of cards include 4 colors (blue, green, yellow, and red), 10 numbers (0 to 9), and special cards (Wild, Wild Draw Four, Draw Two, Skip, and Reverse).

Our implementation wraps [RLCard](http://rlcard.org/games.html#uno) and you can refer to its documentation for additional details. Please cite their work if you use this game in research.

### Observation Space

The observation is a dictionary which contains an `'obs'` element which is the usual RL observation described below, and an  `'action_mask'` which holds the legal moves, described in the Legal Actions Mask section.

The main observation space has a shape of (7, 4, 15). Planes 0-2 represent the current player's hand, while planes 4-6 represent the opponent's hand. For these sets of planes, the first index indicates the number of copies of a card, the second index the color, and the last index the card number (including any special cards). Uno is played with 2 identical decks, so a player can have 0, 1, or 2 copies of a given card, which is why each player has 3 planes to represent their hand.

### Arguments

:param opponents_hand_visible:  Set to `True` to observe the entire observation space as described in `Observation Space` below. Setting it to `False` will remove any observation of the opponent' hands and the observation space will only include planes 0 to 3.

"""

def env(**kwargs):
    env = raw_env(**kwargs)
    env = wrappers.CaptureStdoutWrapper(env)
    env = wrappers.TerminateIllegalWrapper(env, illegal_reward=-1)
    env = wrappers.AssertOutOfBoundsWrapper(env)
    env = wrappers.OrderEnforcingWrapper(env)
    return env


class raw_env(RLCardBase):

    metadata = {'render.modes': ['human'], 'name': 'uno_v4'}

    def __init__(self, opponents_hand_visible=False):
        self._opponents_hand_visible = opponents_hand_visible
        num_planes = 7 if self._opponents_hand_visible else 4
        super().__init__("uno", 2, (num_planes, 4, 15))

    def observe(self, agent):
        obs = self.env.get_state(self._name_to_int(agent))
        if self._opponents_hand_visible:
            observation = obs['obs'].astype(self._dtype)
        else:
            observation = obs['obs'][0:4, :, :].astype(self._dtype)

        legal_moves = self.next_legal_moves
        action_mask = np.zeros(61, 'int8')
        for i in legal_moves:
            action_mask[i] = 1

        return {'observation': observation, 'action_mask': action_mask}

    def render(self, mode='human'):
        for player in self.possible_agents:
            state = self.env.game.get_state(self._name_to_int(player))
            print(f"\n\n=============== {player}'s Hand ===============")
            UnoCard.print_cards(state['hand'])
        print('\n\n================= Target Card =================')
        UnoCard.print_cards(state['target'], wild_color=True)
        print('\n')

    def close(self):
        pass
