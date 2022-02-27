import random

import numpy as np
import rlcard
from gym import spaces
from gym.utils import EzPickle
from rlcard.games.gin_rummy.player import GinRummyPlayer
from rlcard.games.gin_rummy.utils import melding as melding
from rlcard.games.gin_rummy.utils import utils
from rlcard.games.gin_rummy.utils.action_event import GinAction, KnockAction
from rlcard.utils.utils import print_card

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


class raw_env(RLCardBase, EzPickle):

    metadata = {
        "render.modes": ["human"],
        "name": "gin_rummy_v4",
        "is_parallelizable": False,
        "video.frames_per_second": 1,
    }

    def __init__(self, knock_reward: float = 0.5, gin_reward: float = 1.0, opponents_hand_visible=False):
        EzPickle.__init__(self, knock_reward, gin_reward)
        self._opponents_hand_visible = opponents_hand_visible
        num_planes = 5 if self._opponents_hand_visible else 4
        RLCardBase.__init__(self, "gin-rummy", 2, (num_planes, 52))
        self._knock_reward = knock_reward
        self._gin_reward = gin_reward

        self.env.game.judge.scorer.get_payoff = self._get_payoff

    def _get_payoff(self, player: GinRummyPlayer, game) -> float:
        going_out_action = game.round.going_out_action
        going_out_player_id = game.round.going_out_player_id
        if going_out_player_id == player.player_id and type(going_out_action) is KnockAction:
            payoff = self._knock_reward
        elif going_out_player_id == player.player_id and type(going_out_action) is GinAction:
            payoff = self._gin_reward
        else:
            hand = player.hand
            best_meld_clusters = melding.get_best_meld_clusters(hand=hand)
            best_meld_cluster = [] if not best_meld_clusters else best_meld_clusters[0]
            deadwood_count = utils.get_deadwood_count(hand, best_meld_cluster)
            payoff = -deadwood_count / 100
        return payoff

    def observe(self, agent):
        obs = self.env.get_state(self._name_to_int(agent))
        if self._opponents_hand_visible:
            observation = obs['obs'].astype(self._dtype)
        else:
            observation = obs['obs'][0:4, :].astype(self._dtype)

        legal_moves = self.next_legal_moves
        action_mask = np.zeros(110, 'int8')
        for i in legal_moves:
            action_mask[i] = 1

        return {'observation': observation, 'action_mask': action_mask}

    def render(self, mode='human'):
        for player in self.possible_agents:
            state = self.env.game.round.players[self._name_to_int(player)].hand
            print(f"\n===== {player}'s Hand =====")
            print_card([c.__str__()[::-1] for c in state])
        state = self.env.game.get_state(0)
        print("\n==== Top Discarded Card ====")
        print_card([c.__str__() for c in state['top_discard']] if state else None)
        print('\n')
