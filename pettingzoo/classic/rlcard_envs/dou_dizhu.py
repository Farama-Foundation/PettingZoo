from pettingzoo import AECEnv
from pettingzoo.utils.agent_selector import agent_selector
from gym import spaces
import rlcard
import random
import numpy as np
from pettingzoo.utils import wrappers
from .rlcard_base import RLCardBase


def env(**kwargs):
    env = raw_env(**kwargs)
    env = wrappers.TerminateIllegalWrapper(env, illegal_reward=-1)
    env = wrappers.AssertOutOfBoundsWrapper(env)
    pass_move = 308
    env = wrappers.NanNoOpWrapper(env, pass_move, "passing turn with action number {}".format(pass_move))
    env = wrappers.OrderEnforcingWrapper(env)
    return env


class raw_env(RLCardBase):

    metadata = {'render.modes': ['human']}

    def __init__(self):
        self.agents = ['landlord_0', 'peasant_0', 'peasant_1']
        super().__init__("doudizhu", 3, (6, 5, 15))

    def _scale_rewards(self, reward):
        # Maps 1 to 1 and 0 to -1
        return 2 * reward - 1

    def render(self, mode='human'):
        for player in self.agents:
            state = self.env.game.get_state(self._name_to_int(player))
            print("\n===== {}'s Hand ({}) =====".format(player, 'Landlord' if player == 0 else 'Peasant'))
            print(state['current_hand'])
        print('\n=========== Last 3 Actions ===========')
        for action in state['trace'][:-4:-1]:
            print('{}: {}'.format(self._int_to_name(action[0]), action[1]))
        print('\n')
