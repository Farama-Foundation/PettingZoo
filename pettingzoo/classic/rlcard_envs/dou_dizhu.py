import random

import numpy as np
import rlcard
from gym import spaces

from pettingzoo import AECEnv
from pettingzoo.utils import wrappers
from pettingzoo.utils.agent_selector import agent_selector

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
        "name": "dou_dizhu_v4",
        "is_parallelizable": False,
        "video.frames_per_second": 1,
    }

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
