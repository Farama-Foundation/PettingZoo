from .base import BaseWrapper
from gym.spaces import Box
import numpy as np
from ..env_logger import EnvLogger


class ClipOutOfBoundsWrapper(BaseWrapper):
    '''
    this wrapper crops out of bounds actions for Box spaces
    '''
    def __init__(self, env):
        super().__init__(env)
        assert all(isinstance(space, Box) for space in self.action_spaces.values()), "should only use ClipOutOfBoundsWrapper for Box spaces"

    def step(self, action):
        space = self.action_spaces[self.agent_selection]
        if not (action is None and self.dones[self.agent_selection]) and not space.contains(action):
            assert space.shape == action.shape, "action should have shape {}, has shape {}".format(space.shape, action.shape)
            if np.isnan(action).any():
                EnvLogger.error_nan_action()

            EnvLogger.warn_action_out_of_bound(action=action, action_space=space, backup_policy="clipping to space")
            action = np.clip(action, space.low, space.high)

        super().step(action)

    def __str__(self):
        return str(self.env)
