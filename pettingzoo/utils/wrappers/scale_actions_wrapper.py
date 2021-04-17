from .base import BaseWrapper
from gym.spaces import Box, Space, Discrete
import numpy as np
import gym

class scale_actions_wrapper(BaseWrapper):
    '''
    this wrapper expects a scale parameter and scales actions accordingly.
    '''
    def __init__(self, env, scale):
        super().__init__(env)
        self.scale = scale
        new_spaces = {}
        for agent, space in self.action_spaces.items():
            new_low = space.low * scale
            new_high = space.high * scale

            new_spaces[agent] = Box(low=new_low, high=new_high, dtype=new_low.dtype)
        self.action_spaces = new_spaces
        
    def step(self, action, observe = True):
        action = action * self.scale
        return super().step(action, observe)