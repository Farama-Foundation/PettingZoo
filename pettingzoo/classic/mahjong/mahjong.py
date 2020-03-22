from pettingzoo import AECEnv
from pettingzoo.utils.agent_selector import agent_selector
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
        
        self.dones = self._convert_to_dict([False for _ in range(self.num_agents)])
        self.observation_spaces = dict(zip(self.agents, [spaces.Box(low=0.0, high=1.0, shape=(6, 34, 4), dtype=np.bool) for _ in range(self.num_agents)]))
        self.action_spaces = dict(zip(self.agents, [spaces.Discrete(self.env.game.get_action_num()) for _ in range(self.num_agents)]))
        self.infos = self._convert_to_dict([{'legal_moves': []} for _ in range(self.num_agents)])
        
        obs, player_id = self.env.init_game()

        self.agent_order = list(range(self.num_agents))
        self._agent_selector = agent_selector(self.agent_order)
        self.agent_selection = self._agent_selector.reset()
        self.rewards = self._convert_to_dict(self.env.get_payoffs())
        self.infos[player_id]['legal_moves'] = obs['legal_actions']
        
    def _convert_to_dict(self, list_of_list):
        return dict(zip(self.agents, list_of_list))

    def observe(self, agent):
        obs = self.env.get_state(agent)
        return obs['obs']

    def step(self, action, observe=True):
        if self.env.is_over():
            self.rewards = self._convert_to_dict(self.env.get_payoffs())
            self.dones = self._convert_to_dict([True for _ in range(self.num_agents)])
        else:
            obs, next_player_id = self.env.step(action)
            self.prev_player = self.agent_selection
            prev_player_ind = self.agent_order.index(self.prev_player)
            curr_player_ind = self.agent_order.index(next_player_id)
            if next_player_id == self.prev_player:
                self.agent_order.insert(0,self.agent_order.pop(-1))
                
            elif prev_player_ind == self.num_agents-1:
                self.agent_order.remove(next_player_id)
                self.agent_order.insert(0,next_player_id)
            else:
                self.agent_order.remove(next_player_id)
                if curr_player_ind < prev_player_ind:
                    self.agent_order.insert(0,self.agent_order.pop(-1))
                self.agent_order.insert(self.agent_order.index(self.prev_player)+1,next_player_id) 
            skip_agent = prev_player_ind + 1
            self._agent_selector.reinit(self.agent_order)
            for _ in  range(skip_agent):
                self._agent_selector.next()
            self.dones = self._convert_to_dict([True if self.env.is_over() else False for _ in range(self.num_agents)])
            self.infos[next_player_id]['legal_moves'] = obs['legal_actions'] if not self.env.is_over() else [0]
            self.rewards = self._convert_to_dict(self.env.get_payoffs())
        self.agent_selection = self._agent_selector.next()
        if observe:
            return obs['obs'] if obs else None

    def reset(self, observe=True):
        obs, player_id = self.env.init_game()
        self.agent_order = list(range(self.num_agents))
        self._agent_selector.reinit(self.agent_order)
        self.agent_selection = self._agent_selector.reset()
        self.rewards = self._convert_to_dict(self.env.get_payoffs())
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
            print("\n======== Player {}'s Hand ========".format(player))
            print(', '.join([c.get_str() for c in state['current_hand']]))
            print("\nPlayer {}'s Piles: ".format(player),', '.join([c.get_str() for pile in state['players_pile'][player] for c in pile ]))
        print("\n======== Tiles on Table ========")
        print(', '.join([c.get_str() for c in state['table']]))
        print('\n')