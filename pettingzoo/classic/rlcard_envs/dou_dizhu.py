import random

import numpy as np
import rlcard
from gym import spaces

from pettingzoo import AECEnv
from pettingzoo.utils import wrappers
from pettingzoo.utils.agent_selector import agent_selector

from .rlcard_base import RLCardBase

"""
Dou Dizhu, or *Fighting the Landlord*, is a shedding game involving 3 players and a deck of cards plus 2 jokers with suits being irrelevant. Heuristically, one player is designated the "Landlord" and the others become the "Peasants". The objective of the game is to be the first one to have no cards left. If the first person to have no cards left is part of the "Peasant" team, then all members of the "Peasant" team receive a reward (+1). If the "Landlord" wins, then only the "Landlord" receives a reward (+1).

The "Landlord" plays first by putting down a combination of cards. The next player, may pass or put down a higher combination of cards that beat the previous play.

Our implementation wraps [RLCard](http://rlcard.org/games.html#dou-dizhu) and you can refer to its documentation for additional details. Please cite their work if you use this game in research.

### Observation Space

The observation is a dictionary which contains an `'observation'` element which is the usual RL observation described below, and an  `'action_mask'` which holds the legal moves, described in the Legal Actions Mask section.

The main *Observation Space* is encoded in a 1D vector with different concatenated features depending on the agent. To represent a combination of cards a 54-dimensional one-hot vector is encoded as follows. A 4x15 is constructed, where each column represents the rank of the cards (including the two jokers), and each row the number of matching card rank. The matrix is constructed using one-hot encoding. Since there are two jokers in the deck, the six entries that are always zero in the columns of the jokers are removed. Finally, to form the 54-dimensional vector, the one-hot matrix is flatten.
The columns and rows of the 4x15 matrix are encoded as follows:

### Action Space

The raw size of the action space of Dou Dizhu is 27,472. As a reminder, suits are irrelevant in Dou Dizhu.

### Arguments

:param opponents_hand_visible:  Set to `True` to observe the entire observation space as described in `Observation Space` below. Setting it to `False` will remove any observation of the opponent' hands.
"""

def env(**kwargs):
    env = raw_env(**kwargs)
    env = wrappers.CaptureStdoutWrapper(env)
    env = wrappers.TerminateIllegalWrapper(env, illegal_reward=-1)
    env = wrappers.AssertOutOfBoundsWrapper(env)
    env = wrappers.OrderEnforcingWrapper(env)
    return env


class raw_env(RLCardBase):

    metadata = {'render.modes': ['human'], "name": "dou_dizhu_v4"}

    def __init__(self, opponents_hand_visible=False):
        self._opponents_hand_visible = opponents_hand_visible
        self.agents = ['landlord_0', 'peasant_0', 'peasant_1']
        obs_dimension = 901 if self._opponents_hand_visible else 847
        super().__init__("doudizhu", 3, (obs_dimension, ))
        self.observation_spaces = self._convert_to_dict([spaces.Dict(
            {'observation': spaces.Box(low=0.0, high=1.0, shape=(obs_dimension - 111, )
             if agent == 'landlord_0' else (obs_dimension, ), dtype=self._dtype),
             'action_mask': spaces.Box(low=0, high=1, shape=(self.env.num_actions,), dtype=np.int8)})
             for agent in self.agents])

    def _scale_rewards(self, reward):
        # Maps 1 to 1 and 0 to -1
        return 2 * reward - 1

    def observe(self, agent):
        obs = self.env.get_state(self._name_to_int(agent))
        if self._opponents_hand_visible:
            observation = obs['obs'].astype(self._dtype)
        else:
            observation = np.delete(obs['obs'], range(54, 108)).astype(self._dtype)

        legal_moves = self.next_legal_moves
        action_mask = np.zeros(27472, 'int8')
        for i in legal_moves:
            action_mask[i] = 1

        return {'observation': observation, 'action_mask': action_mask}

    def render(self, mode='human'):
        for player in self.possible_agents:
            state = self.env.game.get_state(self._name_to_int(player))
            print(f"\n===== {player}'s Hand =====")
            print(state['current_hand'])
        print('\n=========== Last 3 Actions ===========')
        for action in state['trace'][:-4:-1]:
            print(f'{self._int_to_name(action[0])}: {action[1]}')
        print('\n')
