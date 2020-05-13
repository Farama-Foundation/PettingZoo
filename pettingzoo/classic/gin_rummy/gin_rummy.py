from pettingzoo import AECEnv
from pettingzoo.utils.agent_selector import agent_selector
from gym import spaces
import random
import rlcard
from rlcard.utils.utils import print_card
from rlcard.games.gin_rummy.player import GinRummyPlayer
from rlcard.games.gin_rummy.utils import utils
from rlcard.games.gin_rummy.utils.action_event import KnockAction, GinAction
import rlcard.games.gin_rummy.utils.melding as melding
import numpy as np
from pettingzoo.utils import wrappers


def env(**kwargs):
    env = raw_env(**kwargs)
    env = wrappers.TerminateIllegalWrapper(env, illegal_reward=-1)
    env = wrappers.AssertOutOfBoundsWrapper(env)
    env = wrappers.NaNRandomWrapper(env)
    env = wrappers.OrderEnforcingWrapper(env)
    return env


class raw_env(AECEnv):

    metadata = {'render.modes': ['human']}

    def __init__(self, seed=None, knock_reward: float = 0.5, gin_reward: float = 1.0):
        super().__init__()
        self._knock_reward = knock_reward
        self._gin_reward = gin_reward
        self.env = rlcard.make('gin-rummy', config={"seed": seed})
        self.agents = ['player_0', 'player_1']
        self.num_agents = len(self.agents)
        self.has_reset = False

        self.observation_spaces = self._convert_to_dict([spaces.Box(low=0.0, high=1.0, shape=(5, 52), dtype=np.bool) for _ in range(self.num_agents)])
        self.action_spaces = self._convert_to_dict([spaces.Discrete(self.env.game.get_action_num()) for _ in range(self.num_agents)])

        self.agent_order = self.agents
        self._agent_selector = agent_selector(self.agent_order)
        self.env.game.judge.scorer.get_payoff = self._get_payoff

    def _int_to_name(self, ind):
        return self.agents[ind]

    def _name_to_int(self, name):
        return self.agents.index(name)

    def _convert_to_dict(self, list_of_list):
        return dict(zip(self.agents, list_of_list))

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
        return obs['obs']

    def step(self, action, observe=True):
        obs, next_player_id = self.env.step(action)
        next_player = self._int_to_name(next_player_id)
        self._last_obs = obs['obs']
        self.prev_player = self.agent_selection
        prev_player_ind = self.agent_order.index(self.prev_player)
        curr_player_ind = self.agent_order.index(next_player)
        if next_player == self.prev_player:
            self.agent_order.insert(0, self.agent_order.pop(-1))
        elif prev_player_ind == self.num_agents - 1:
            self.agent_order.remove(next_player)
            self.agent_order.insert(0, next_player)
        else:
            self.agent_order.remove(next_player)
            if curr_player_ind < prev_player_ind:
                self.agent_order.insert(0, self.agent_order.pop(-1))
            self.agent_order.insert(self.agent_order.index(self.prev_player) + 1, next_player)
        skip_agent = prev_player_ind + 1
        self._agent_selector.reinit(self.agent_order)
        for _ in range(skip_agent):
            self._agent_selector.next()
        if self.env.is_over():
            self.rewards = self._convert_to_dict(self.env.get_payoffs())
            self.infos[next_player]['legal_moves'] = [4]
            self.dones = self._convert_to_dict([True if self.env.is_over() else False for _ in range(self.num_agents)])
        else:
            self.infos[next_player]['legal_moves'] = obs['legal_actions']
        self.agent_selection = self._agent_selector.next()
        if observe:
            return obs['obs'] if obs else self._last_obs

    def reset(self, observe=True):
        self.has_reset = True
        obs, player_id = self.env.reset()
        self.agent_order = [self._int_to_name(agent) for agent in [player_id, 0 if player_id == 1 else 1]]
        self._agent_selector.reinit(self.agent_order)
        self.agent_selection = self._agent_selector.reset()
        self.rewards = self._convert_to_dict(np.array([0.0, 0.0]))
        self.dones = self._convert_to_dict([False for _ in range(self.num_agents)])
        self.infos = self._convert_to_dict([{'legal_moves': []} for _ in range(self.num_agents)])
        self.infos[self._int_to_name(player_id)]['legal_moves'] = obs['legal_actions']
        self._last_obs = obs['obs']
        if observe:
            return obs['obs']
        else:
            return

    def render(self, mode='human'):
        for player in self.agents:
            state = self.env.game.round.players[self._name_to_int(player)].hand
            print("\n===== {}'s Hand =====".format(player))
            print_card([c.__str__()[::-1] for c in state])
        state = self.env.game.get_state(0)
        print("\n==== Top Discarded Card ====")
        print_card([c.__str__() for c in state['top_discard']] if state else None)
        print('\n')

    def close(self):
        pass
