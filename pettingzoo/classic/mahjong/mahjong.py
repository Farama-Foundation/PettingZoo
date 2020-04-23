from pettingzoo import AECEnv
from pettingzoo.utils.agent_selector import agent_selector
from gym import spaces
import rlcard
import numpy as np


class env(AECEnv):

    metadata = {'render.modes': ['human']}

    def __init__(self, **kwargs):
        super(env, self).__init__()
        self.env = rlcard.make('mahjong', **kwargs)
        self.agents = ['player_0', 'player_1', 'player_2', 'player_3']
        self.num_agents = len(self.agents)

        self.dones = self._convert_to_dict([False for _ in range(self.num_agents)])
        self.observation_spaces = self._convert_to_dict([spaces.Box(low=0.0, high=1.0, shape=(6, 34, 4), dtype=np.bool) for _ in range(self.num_agents)])
        self.action_spaces = self._convert_to_dict([spaces.Discrete(self.env.game.get_action_num()) for _ in range(self.num_agents)])
        self.infos = self._convert_to_dict([{'legal_moves': []} for _ in range(self.num_agents)])

        obs, player_id = self.env.init_game()

        self._last_obs = obs['obs']
        self.agent_order = ['player_0', 'player_1', 'player_2', 'player_3']
        self._agent_selector = agent_selector(self.agent_order)
        self.agent_selection = self._agent_selector.reset()
        self.rewards = self._convert_to_dict(self.env.get_payoffs())
        self.infos[self._int_to_name(player_id)]['legal_moves'] = obs['legal_actions']

    def _int_to_name(self, ind):
        return self.agents[ind]

    def _name_to_int(self, name):
        return self.agents.index(name)

    def _convert_to_dict(self, list_of_list):
        return dict(zip(self.agents, list_of_list))

    def observe(self, agent):
        obs = self.env.get_state(self._name_to_int(agent))
        return obs['obs']

    def step(self, action, observe=True):
        if self.dones[self.agent_selection]:
            self.dones = self._convert_to_dict([True for _ in range(self.num_agents)])
            obs = False
        else:
            if action not in self.infos[self.agent_selection]['legal_moves']:
                self.rewards[self.agent_selection] = -1
                self.dones = self._convert_to_dict([True for _ in range(self.num_agents)])
                info_copy = self.infos[self.agent_selection]
                self.infos = self._convert_to_dict([{'legal_moves': [37]} for agent in range(self.num_agents)])
                self.infos[self.agent_selection] = info_copy
                self.agent_selection = self._agent_selector.next()
                return self._last_obs
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
                self.infos[next_player]['legal_moves'] = [37]
                self.dones = self._convert_to_dict([True if self.env.is_over() else False for _ in range(self.num_agents)])
            else:
                self.infos[next_player]['legal_moves'] = obs['legal_actions']
        self.agent_selection = self._agent_selector.next()
        if observe:
            return obs['obs'] if obs else self._last_obs

    def reset(self, observe=True):
        obs, player_id = self.env.init_game()
        self.agent_order = ['player_0', 'player_1', 'player_2', 'player_3']
        self._agent_selector.reinit(self.agent_order)
        self.agent_selection = self._agent_selector.reset()
        self.rewards = self._convert_to_dict(self.env.get_payoffs())
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
            state = self.env.game.get_state(self._name_to_int(player))
            print("\n======== {}'s Hand ========".format(player))
            print(', '.join([c.get_str() for c in state['current_hand']]))
            print("\n{}'s Piles: ".format(player), ', '.join([c.get_str() for pile in state['players_pile'][self._name_to_int(player)] for c in pile]))
        print("\n======== Tiles on Table ========")
        print(', '.join([c.get_str() for c in state['table']]))
        print('\n')

    def close(self):
        pass
