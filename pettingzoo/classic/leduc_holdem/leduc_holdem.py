from pettingzoo import AECEnv
from gym import spaces
import rlcard
import numpy as np

class env(AECEnv):

    def __init__(self,**kwargs):
        super(env, self).__init__()
        self.env = rlcard.make('leduc-holdem',**kwargs)
        self.num_agents = 2
        self.agents = list(range(self.num_agents))
        self.reset()
        self.observation_spaces = dict(zip(self.agents, [spaces.MultiDiscrete(6*[2]) for _ in range(self.num_agents)]))
        self.action_spaces = dict(zip(self.agents, [spaces.Discrete(self.env.game.get_action_num()) for _ in range(self.num_agents)]))
        self.dones = self.convert_to_dict([False for _ in range(self.num_agents)])
        self.infos = self.convert_to_dict(['' for _ in range(self.num_agents)])
    
    def convert_to_dict(self, list_of_list):
        return dict(zip(self.agents, list_of_list))

    def decode_action(self, action):
        return self.env.decode_action(action)

    def observe(self, agent):
        obs = self.env.get_state(agent)
        return obs['obs']

    def step(self, action, observe=True):
        obs, next_player_id = self.env.step(action)
        self.agent_selection = next_player_id
        self.dones = self.convert_to_dict([True if self.env.is_over() else False for _ in range(self.num_agents)])
        self.valid_action_space = obs['legal_actions']
        if self.env.is_over():
            self.rewards = self.convert_to_dict(self.env.get_payoffs())
        else:
            self.rewards = self.convert_to_dict(np.array([0.0, 0.0]))
        if observe:
            return obs['obs']
        else:
            return

    def reset(self, observe=True):
        obs, player_id = self.env.init_game()
        self.agent_selection = player_id
        self.agent_order = [player_id, 0 if player_id==1 else 1]
        self.valid_action_space = obs['legal_actions']
        self.rewards = self.convert_to_dict(np.array([0.0, 0.0]))
        if observe:
            return obs['obs']
        else:
            return
