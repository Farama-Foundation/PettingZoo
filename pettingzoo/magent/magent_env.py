from gym.spaces import Discrete
import numpy as np
import warnings
import magent
from pettingzoo import AECEnv


class env(AECEnv):
    metadata = {'render.modes': ['human']}
    '''
    Parent Class Methods
    '''
    def __init__(self, config, **kwargs):
        self.env = magent.GridWorld(config, **kwargs)
        self.num_agents = 2
        self.agents = ["predator", "prey"]
        self.dones = {agent: False for agent in self.agents}
        self.agent_order = self.agents[:]

        self.action_spaces = {agent: Discrete(3) for agent in self.agents}
        self.observation_spaces = {agent: Discrete(4) for agent in self.agents}

        self.display_wait = 0.0
        self.rewards = {agent: 0 for agent in self.agents}
        self.dones = {agent: False for agent in self.agents}
        self.infos = {agent: {} for agent in self.agents}
        self.num_moves = 0

    def step(self, action, observe=True):
        self.env.step()

    def reset(self, observe=True):
        self.env.reset()

    def observe(self, agent):
        return self.env.get_observation(agent)

    def last(self):
        pass

    def render(self, mode='human'):
        self.env.render()

    def close(self):
        pass

    '''
    Child Class Methods
    '''
    def add_walls(self, method, **kwargs):
        self.env.add_walls(method, **kwargs)

    def new_group(self, name):
        return self.env.new_group(name)

    def add_agents(self, handle, method, **kwargs):
        return self.env.add_agents(handle, method, **kwargs)

    def set_action(self, handle, actions):
        self.env.set_action(handle, actions)

    def get_reward(self, handle):
        self.env.get_reward(handle)

    def clear_dead(self):
        self.env.clear_dead()

    def get_handles(self):
        return self.env.get_handles()

    def get_num_agents(self, handle):
        return self.env.get_num(handle)

    def get_action_space(self, handle):
        return self.env.get_action_space(handle)

    def get_view_space(self, handle):
        return self.env.get_view_space(handle)

    def get_feature_space(self, handle):
        return self.env.get_feature_space(handle)

    def get_agent_id(self, handle):
        return self.env.get_agent_id(handle)

    def get_alive(self, handle):
        return self.env.get_alive(handle)

    def get_pos(self, handle):
        return self.env.get_pos(handle)

    def get_view2attack(self, handle):
        return self.env.get_view2attack(handle)

    def get_global_minimap(self, height, width):
        return self.env.get_global_minimap(height, width)

    def set_seed(self, seed):
        self.env.set_seed(seed)

    def set_render_dir(self, name):
        self.env.set_render_dir(name)
