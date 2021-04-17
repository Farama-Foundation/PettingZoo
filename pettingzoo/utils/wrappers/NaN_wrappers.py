from .base import BaseWrapper
import numpy as np
import gym
from gym import spaces
from gym.spaces import Box, Discrete
import warnings
import random


class nan_noop_wrapper(BaseWrapper):
    '''
    this wrapper expects there to be a no_op_action parameter which
    is the action to take in cases when nothing should be done.
    '''
    def step(self, action, no_op_action, observe = True):
        if np.isnan(action).any():
            warnings.warn("[WARNING]: Step received an NaN action {}. Evironment is {}. Taking no operation action.".format(action, self))
            action = no_op_action
        return super().step(action, observe)

class nan_zeros_wrapper(BaseWrapper):
    '''
    this wrapper warns and executes a zeros action when nothing should be done.
    Only for Box action spaces.
    '''
    def step(self, action, observe=True):
        if np.isnan(action).any():
            warnings.warn("[WARNING]: Step received an NaN action {}. Environment is {}. Taking the all zeroes action.".format(action, self))
            action = np.zeros_like(action)
        return super().step(action, observe)


class nan_random_wrapper(BaseWrapper):
    '''
    this wrapper takes a random action
    '''
    def step(self, action, observe=True):
        if np.isnan(action).any():
            obs = self.env.last()
            if isinstance(obs, dict) and 'action mask' in obs:
                warnings.warn("[WARNING]: Step received an NaN action {}. Environment is {}. Taking a random action from 'action mask'.".format(action, self))
                action = self.np_random.choice(np.flatnonzero(obs['action_mask']))
            else:
                warnings.warn("[WARNING]: Step received an NaN action {}. Environment is {}. Taking a random action.".format(action, self))
                action = self.action_spaces[self.agent_selection].sample()
        return super().step(action, observe)

    def seed(self, seed=None):
        self.np_random, seed = gym.utils.seeding.np_random(seed)
        super().seed(seed)
