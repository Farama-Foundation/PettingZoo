import numpy as np

#################################################################
# Implements multi-agent controllers
#################################################################


class RandomPolicy(object):

    # constructor
    def __init__(self, n_actions, rng):
        self.rng = rng
        self.n_actions = n_actions

    def set_rng(self, rng):
        self.rng = rng

    def act(self, state):
        return self.rng.randint(self.n_actions)


class SingleActionPolicy(object):

    def __init__(self, a):
        self.action = a

    def act(self, state):
        return self.action
