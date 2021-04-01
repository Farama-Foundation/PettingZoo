from pettingzoo import AECEnv
from pettingzoo.utils.agent_selector import agent_selector
from gym import spaces
import rlcard
import random
from rlcard.games.uno.card import UnoCard
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

    metadata = {'render.modes': ['human'], 'name': 'uno_v3'}

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
        action_mask = np.zeros(61, int)
        for i in legal_moves:
            action_mask[i] = 1

        return {'observation': observation, 'action_mask': action_mask}

    def render(self, mode='human'):
        for player in self.possible_agents:
            state = self.env.game.get_state(self._name_to_int(player))
            print("\n\n=============== {}'s Hand ===============".format(player))
            UnoCard.print_cards(state['hand'])
        print('\n\n================= Target Card =================')
        UnoCard.print_cards(state['target'], wild_color=True)
        print('\n')

    def close(self):
        pass
