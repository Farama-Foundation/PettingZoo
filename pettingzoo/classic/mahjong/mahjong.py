from pettingzoo import AECEnv
from gym import spaces
import rlcard
import numpy as np

class env(AECEnv):

    metadata = {'render.modes': ['human']}

    def __init__(self,**kwargs):
        super(env, self).__init__()
        self.env = rlcard.make('mahjong',**kwargs)
        self.num_agents = 4
        self.agents = list(range(self.num_agents))
        
        self.reset()

        self.observation_spaces = dict(zip(self.agents, [spaces.Box(low=0.0, high=1.0, shape=(6, 34, 4), dtype=np.bool) for _ in range(self.num_agents)]))
        self.action_spaces = dict(zip(self.agents, [spaces.Discrete(self.env.game.get_action_num()) for _ in range(self.num_agents)]))

    def _convert_to_dict(self, list_of_list):
        return dict(zip(self.agents, list_of_list))

    def observe(self, agent):
        obs = self.env.get_state(agent)
        return obs['obs']

    def step(self, action, observe=True):
        obs, next_player_id = self.env.step(action)
        self.prev_player = self.agent_selection
        self.agent_selection = next_player_id
        prev_player_ind = self.agent_order.index(self.prev_player)
        curr_player_ind = self.agent_order.index(self.agent_selection)
        if self.agent_selection == self.prev_player:
            self.agent_order.insert(0,self.agent_order.pop(-1))
        elif prev_player_ind == self.num_agents-1:
            self.agent_order.remove(self.agent_selection)
            self.agent_order.insert(0,self.agent_selection) 
        else:
            self.agent_order.remove(self.agent_selection)
            if curr_player_ind < prev_player_ind:
                self.agent_order.insert(0,self.agent_order.pop(-1))
            self.agent_order.insert(self.agent_order.index(self.prev_player)+1,self.agent_selection) 
        self.dones = self._convert_to_dict([True if self.env.is_over() else False for _ in range(self.num_agents)])
        self.infos[next_player_id]['legal_moves'] = obs['legal_actions']
        self.rewards = self._convert_to_dict(self.env.get_payoffs())
        if observe:
            return obs['obs']
        else:
            return

    def reset(self, observe=True):
        obs, player_id = self.env.init_game()
        self.agent_selection = player_id
        self.agent_order = list(range(self.num_agents))
        self.rewards = self._convert_to_dict(self.env.get_payoffs())
        self.dones = self._convert_to_dict([False for _ in range(self.num_agents)])
        self.infos = self._convert_to_dict([{'legal_moves': []} for _ in range(self.num_agents)])
        self.infos[player_id]['legal_moves'] = obs['legal_actions']
        if observe:
            return obs['obs']
        else:
            return

    def render(self, mode='human'):
        state = self.env.game.get_state(self.agent_selection)
        print("\n===== Player {}'s Hand =====".format(self.agent_selection))
        print(', '.join([c.get_str() for c in state['current_hand']]))
        print("\n===== Tiles on Table =====".format(self.agent_selection))
        print(', '.join([c.get_str() for c in state['table']]))
        print("\n===== Public Piles =====".format(self.agent_selection))
        for player in range(self.num_agents):
            print('Player {}:'.format(player),', '.join([c.get_str() for pile in state['players_pile'][player] for c in pile ]))
        print('\n')
