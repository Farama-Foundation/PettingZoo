import numpy as np
import warnings
import magent
from pettingzoo import AECEnv

class env(AECEnv):

    metadata = {'render.modes': ['human']}
    '''
    Parent Class Methods
    '''
    def __init__(self):
        pass

    def __init__(self, config, **kwargs):
        self.env = magent.GridWorld(config, **kwargs)

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
