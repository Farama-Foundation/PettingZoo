import abc

import numpy as np

#################################################################
# Implements multi-agent controllers
#################################################################


class PursuitPolicy(abc.ABC):
    @abc.abstractmethod
    def act(self, state: np.ndarray) -> int:
        raise NotImplementedError


class RandomPolicy(PursuitPolicy):

    # constructor
    def __init__(self, n_actions, rng):
        self.rng = rng
        self.n_actions = n_actions

    def set_rng(self, rng):
        self.rng = rng

    def act(self, state):
        return self.rng.integers(self.n_actions)


class SingleActionPolicy(PursuitPolicy):
    def __init__(self, a):
        self.action = a

    def act(self, state):
        return self.action
