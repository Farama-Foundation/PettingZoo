from pettingzoo import AECEnv
from pettingzoo.utils.agent_selector import agent_selector
from gym import spaces
import rlcard
from rlcard.utils.utils import print_card
import numpy as np


class env(AECEnv):

    metadata = {'render.modes': ['human']}

    def __init__(self, **kwargs):
        super(env, self).__init__()
        self.env = rlcard.make('leduc-holdem', **kwargs)
        self.num_agents = 2
        self.agents = list(range(self.num_agents))

        self.rewards = self._convert_to_dict(np.array([0.0, 0.0]))
        self.dones = self._convert_to_dict([False for _ in range(self.num_agents)])
        self.infos = self._convert_to_dict([{'legal_moves': []} for _ in range(self.num_agents)])
        self.observation_spaces = dict(zip(self.agents, [spaces.Box(low=0.0, high=1.0, shape=(34,), dtype=np.bool) for _ in range(self.num_agents)]))
        self.action_spaces = dict(zip(self.agents, [spaces.Discrete(self.env.game.get_action_num()) for _ in range(self.num_agents)]))

        obs, player_id = self.env.init_game()

        self.agent_order = [player_id, 0 if player_id == 1 else 1]
        self._agent_selector = agent_selector(self.agent_order)
        self.agent_selection = self._agent_selector.reset()
        self.infos[player_id]['legal_moves'] = obs['legal_actions']

    def _convert_to_dict(self, list_of_list):
        return dict(zip(self.agents, list_of_list))

    def _decode_action(self, action):
        return self.env._decode_action(action)

    def observe(self, agent):
        obs = self.env.get_state(agent)
        return obs['obs']

    def step(self, action, observe=True):
        if self.env.is_over():
            self.rewards = self._convert_to_dict(self.env.get_payoffs())
            self.dones = self._convert_to_dict([True for _ in range(self.num_agents)])
            obs = False
        else:
            obs, next_player_id = self.env.step(action)
            self.infos[next_player_id]['legal_moves'] = obs['legal_actions']
            if self.env.is_over():
                self.dones = self._convert_to_dict([True for _ in range(self.num_agents)])
                self.rewards = self._convert_to_dict(self.env.get_payoffs())
                self._last_obs = obs['obs']
                self.infos[next_player_id]['legal_moves'] = [0]
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
        if observe:
            return obs['obs']
        else:
            return

    def render(self, mode='human'):
        for player in self.agents:
            state = self.env.game.get_state(player)
            print("\n=============== Player {}'s Hand ===============".format(player))
            print_card(state['hand'])
            print("\nPlayer {}'s Chips: {}".format(player, state['my_chips']))
        print('\n================= Public Cards =================')
        print_card(state['public_card']) if state['public_card'] is not None else print('No public cards.')
        print('\n')
