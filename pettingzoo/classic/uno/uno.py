from pettingzoo import AECEnv
from pettingzoo.utils.agent_selector import agent_selector
from gym import spaces
import rlcard
from rlcard.games.uno.card import UnoCard
import numpy as np


class env(AECEnv):

    metadata = {'render.modes': ['human']}

    def __init__(self, **kwargs):
        super(env, self).__init__()
        self.env = rlcard.make('uno', **kwargs)
        self.num_agents = 2
        self.agents = list(range(self.num_agents))

        self.rewards = self._convert_to_dict(np.array([0.0, 0.0]))
        self.dones = self._convert_to_dict([False for _ in range(self.num_agents)])
        self.infos = self._convert_to_dict([{'legal_moves': []} for _ in range(self.num_agents)])
        self.observation_spaces = dict(zip(self.agents, [spaces.Box(low=0.0, high=1.0, shape=(7, 4, 15), dtype=np.bool) for _ in range(self.num_agents)]))
        self.action_spaces = dict(zip(self.agents, [spaces.Discrete(self.env.game.get_action_num()) for _ in range(self.num_agents)]))

        obs, player_id = self.env.init_game()

        self._last_obs = obs['obs']
        self.agent_order = [player_id, 0 if player_id == 1 else 1]
        self._agent_selector = agent_selector(self.agent_order)
        self.agent_selection = self._agent_selector.reset()
        self.infos[player_id]['legal_moves'] = obs['legal_actions']

    def _convert_to_dict(self, list_of_list):
        return dict(zip(self.agents, list_of_list))

    def observe(self, agent):
        obs = self.env.get_state(agent)
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
                self.infos = self._convert_to_dict([{'legal_moves': [60]} for agent in range(self.num_agents)])
                self.infos[self.agent_selection] = info_copy
                self.agent_selection = self._agent_selector.next()
                return self._last_obs
            obs, next_player_id = self.env.step(action)
            if self.env.is_over():
                self.dones = self._convert_to_dict([True for _ in range(self.num_agents)])
                self.rewards = self._convert_to_dict(self.env.get_payoffs())
                self._last_obs = obs['obs']
                self.infos[next_player_id]['legal_moves'] = [60]
            else:
                self.prev_player = self.agent_selection
                if next_player_id == self.prev_player:
                    self.agent_order.insert(0, self.agent_order.pop(-1))
                    skip_agent = 1
                else:
                    self.agent_order = [next_player_id, 0 if next_player_id == 1 else 1]
                    skip_agent = 0
                self.infos[next_player_id]['legal_moves'] = obs['legal_actions']
                self._agent_selector.reinit(self.agent_order)
                for _ in range(skip_agent):
                    self._agent_selector.next()
        self.agent_selection = self._agent_selector.next()
        if observe:
            return obs['obs'] if obs else self._last_obs

    def reset(self, observe=True):
        obs, player_id = self.env.init_game()
        self.agent_order = [player_id, 0 if player_id == 1 else 1]
        self._agent_selector.reinit(self.agent_order)
        self.agent_selection = self._agent_selector.reset()
        self.rewards = self._convert_to_dict(np.array([0.0, 0.0]))
        self.dones = self._convert_to_dict([False for _ in range(self.num_agents)])
        self.infos = self._convert_to_dict([{'legal_moves': []} for _ in range(self.num_agents)])
        self.infos[player_id]['legal_moves'] = obs['legal_actions']
        self._last_obs = obs['obs']
        if observe:
            return obs['obs']
        else:
            return

    def render(self, mode='human'):
        for player in self.agents:
            state = self.env.game.get_state(player)
            print("\n\n=============== Player {}'s Hand ===============".format(player))
            UnoCard.print_cards(state['hand'])
        print('\n\n================= Target Card =================')
        UnoCard.print_cards(state['target'], wild_color=True)
        print('\n')
