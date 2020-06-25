import numpy as np
import copy
from gym.spaces import Box, Discrete
from gym import spaces
import warnings
from pettingzoo import AECEnv

from .env_logger import EnvLogger


class BaseWrapper(AECEnv):
    '''
    Creates a wrapper around `env` parameter. Extend this class
    to create a useful wrapper.
    '''
    metadata = {'render.modes': ['human']}

    def __init__(self, env):
        super().__init__()
        self.env = env

        self.num_agents = self.env.num_agents
        self.agents = self.env.agents
        self.observation_spaces = self.env.observation_spaces
        self.action_spaces = self.env.action_spaces

        # we don't want these defined as we don't want them used before they are gotten

        # self.agent_selection = self.env.agent_selection

        # self.rewards = self.env.rewards
        # self.dones = self.env.dones

        # we don't want to care one way or the other whether environments have an infos or not before reset
        try:
            self.infos = self.env.infos
        except AttributeError:
            pass

    def close(self):
        self.env.close()

    def render(self, mode='human'):
        self.env.render(mode)

    def reset(self, observe=True):
        observation = self.env.reset(observe)

        self.agent_selection = self.env.agent_selection
        self.rewards = self.env.rewards
        self.dones = self.env.dones
        self.infos = self.env.infos

        return observation

    def observe(self, agent):
        return self.env.observe(agent)

    def step(self, action, observe=True):
        next_obs = self.env.step(action, observe=observe)

        self.agent_selection = self.env.agent_selection
        self.rewards = self.env.rewards
        self.dones = self.env.dones
        self.infos = self.env.infos

        return next_obs


class TerminateIllegalWrapper(BaseWrapper):
    '''
    this wrapper terminates the game with the current player losing
    in case of illegal values

    parameters:
        - illegal_reward: number that is the value of the player making an illegal move.
    '''
    def __init__(self, env, illegal_reward):
        super().__init__(env)
        self._illegal_value = illegal_reward

    def step(self, action, observe=True):
        current_agent = self.agent_selection
        assert 'legal_moves' in self.infos[current_agent], "Illegal moves must always be defined to use the TerminateIllegalWrapper"
        if action not in self.infos[current_agent]['legal_moves']:
            EnvLogger.warn_on_illegal_move()
            self.dones = {d: True for d in self.dones}
            for info in self.infos.values():
                info['legal_moves'] = []
            self.rewards = {d: 0 for d in self.dones}
            self.rewards[current_agent] = self._illegal_value
        else:
            return super().step(action, observe)


class NanNoOpWrapper(BaseWrapper):
    '''
    this wrapper expects there to be a no_op_action parameter which
    is the action to take in cases when nothing should be done.
    '''
    def __init__(self, env, no_op_action, no_op_policy):
        super().__init__(env)
        self._no_op_action = no_op_action
        self._no_op_policy = no_op_policy

    def step(self, action, observe=True):
        if np.isnan(action).any():
            EnvLogger.warn_action_is_NaN(self._no_op_policy)
            action = self._no_op_action
        return super().step(action, observe)


class NanZerosWrapper(BaseWrapper):
    '''
    this wrapper warns and executes a zeros action when nothing should be done.
    Only for Box action spaces.
    '''
    def __init__(self, env):
        super().__init__(env)
        assert all(isinstance(space, Box) for space in self.action_spaces.values()), "should only use NanZerosWrapper for Box spaces. Use NanNoOpWrapper for discrete spaces"

    def step(self, action, observe=True):
        if np.isnan(action).any():
            EnvLogger.warn_action_is_NaN("taking the all zeros action")
            action = np.zeros_like(action)
        return super().step(action, observe)


class NaNRandomWrapper(BaseWrapper):
    '''
    this wrapper takes a random action
    '''
    def __init__(self, env):
        super().__init__(env)
        assert all(isinstance(space, Discrete) for space in env.action_spaces.values()), "action space should be discrete for NaNRandomWrapper"
        SEED = 0x33bb9cc9
        self.np_random = np.random.RandomState(SEED)

    def step(self, action, observe=True):
        if np.isnan(action).any():
            cur_info = self.infos[self.agent_selection]
            if 'legal_moves' in cur_info:
                backup_policy = "taking a random legal action"
                EnvLogger.warn_action_is_NaN(backup_policy)
                action = self.np_random.choice(cur_info['legal_moves'])
            else:
                backup_policy = "taking a random action"
                EnvLogger.warn_action_is_NaN(backup_policy)
                act_space = self.action_spaces[self.agent_selection]
                action = self.np_random.choice(act_space.n)

        return super().step(action, observe)


class AssertOutOfBoundsWrapper(BaseWrapper):
    '''
    this wrapper crashes for out of bounds actions
    Should be used for Discrete spaces
    '''
    def __init__(self, env):
        super().__init__(env)
        assert all(isinstance(space, Discrete) for space in self.action_spaces.values()), "should only use AssertOutOfBoundsWrapper for Discrete spaces"

    def step(self, action, observe=True):
        assert self.action_spaces[self.agent_selection].contains(action), "action is not in action space"
        return super().step(action, observe)


class ClipOutOfBoundsWrapper(BaseWrapper):
    '''
    this wrapper crops out of bounds actions for Box spaces
    '''
    def __init__(self, env):
        super().__init__(env)
        assert all(isinstance(space, Box) for space in self.action_spaces.values()), "should only use ClipOutOfBoundsWrapper for Box spaces"

    def step(self, action, observe=True):
        space = self.action_spaces[self.agent_selection]
        if not space.contains(action):
            assert space.shape == action.shape, "action should have shape {}, has shape {}".format(space.shape, action.shape)

            EnvLogger.warn_action_out_of_bound(action=action, action_space=space, backup_policy="clipping to space")
            action = np.clip(action, space.low, space.high)

        return super().step(action, observe)


class OrderEnforcingWrapper(BaseWrapper):
    '''
    check all orders:

    * error on getting rewards, dones, infos, agent_selection before reset
    * error on calling step, observe before reset
    * warn on calling close before render or reset
    * warn on calling step after environment is done
    '''
    def __init__(self, env):
        self._has_reset = False
        self._has_rendered = False
        self._has_updated = False
        super().__init__(env)

    def __getattr__(self, value):
        '''
        raises an error message when data is gotten from the env
        which should only be gotten after reset
        '''
        if value == "agent_order":
            raise AttributeError("agent_order has been removed from the API. Please consider using agent_iter instead.")
        elif value in {"rewards", "dones", "infos", "agent_selection"}:
            EnvLogger.error_field_before_reset(value)
            return None
        else:
            raise AttributeError("'{}' object has no attribute '{}'".format(type(self).__name__, value))

    def render(self, mode='human'):
        if not self._has_reset:
            EnvLogger.error_render_before_reset()
        self._has_rendered = True
        super().render(mode)

    def close(self):
        super().close()
        if not self._has_rendered:
            EnvLogger.warn_close_unrendered_env()
        if not self._has_reset:
            EnvLogger.warn_close_before_reset()

        self._has_rendered = False
        self._has_reset = False

    def step(self, action, observe=True):
        self._has_updated = True
        if not self._has_reset:
            EnvLogger.error_step_before_reset()
        elif self.dones[self.agent_selection]:
            EnvLogger.warn_step_after_done()
            self.dones = {agent: True for agent in self.dones}
            self.rewards = {agent: 0 for agent in self.rewards}
            return super().observe(self.agent_selection) if observe else None
        else:
            return super().step(action, observe)

    def observe(self, agent):
        if not self._has_reset:
            EnvLogger.error_observe_before_reset()
        return super().observe(agent)

    def reset(self, observe=True):
        self._has_updated = True
        self._has_reset = True
        return super().reset(observe)
