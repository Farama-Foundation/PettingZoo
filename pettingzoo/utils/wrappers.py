import numpy as np
import copy
from gym.spaces import Box, Discrete
from gym import spaces
import warnings
from pettingzoo import AECEnv

from .env_logger import EnvLogger
from .capture_stdout import capture_stdout


class BaseWrapper(AECEnv):
    '''
    Creates a wrapper around `env` parameter. Extend this class
    to create a useful wrapper.
    '''

    def __init__(self, env):
        super().__init__()
        self.env = env

        self.observation_spaces = self.env.observation_spaces
        self.action_spaces = self.env.action_spaces
        self.possible_agents = self.env.possible_agents
        self.metadata = self.env.metadata

        # we don't want these defined as we don't want them used before they are gotten

        # self.agent_selection = self.env.agent_selection

        # self.rewards = self.env.rewards
        # self.dones = self.env.dones

        # we don't want to care one way or the other whether environments have an infos or not before reset
        try:
            self.infos = self.env.infos
        except AttributeError:
            pass

    def seed(self, seed=None):
        self.env.seed(seed)

    def close(self):
        self.env.close()

    def render(self, mode='human'):
        return self.env.render(mode)

    def reset(self):
        self.env.reset()

        self.agent_selection = self.env.agent_selection
        self.rewards = self.env.rewards
        self.dones = self.env.dones
        self.infos = self.env.infos
        self.agents = self.env.agents
        self._cumulative_rewards = self.env._cumulative_rewards

    def observe(self, agent):
        return self.env.observe(agent)

    def step(self, action):
        self.env.step(action)

        self.agent_selection = self.env.agent_selection
        self.rewards = self.env.rewards
        self.dones = self.env.dones
        self.infos = self.env.infos
        self.agents = self.env.agents
        self._cumulative_rewards = self.env._cumulative_rewards


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
        self._prev_obs = None

    def reset(self):
        self._terminated = False
        self._prev_obs = None
        super().reset()

    def observe(self, agent):
        obs = super().observe(agent)
        self._prev_obs = obs
        return obs

    def step(self, action):
        current_agent = self.agent_selection
        if self._prev_obs is None:
            self.observe(self.agent_selection)
        assert 'action_mask' in self._prev_obs, "action_mask must always be part of environment observation as an element in a dictionary observation to use the TerminateIllegalWrapper"
        _prev_action_mask = self._prev_obs['action_mask']
        self._prev_obs = None
        if self._terminated and self.dones[self.agent_selection]:
            self._was_done_step(action)
        elif not self.dones[self.agent_selection] and not _prev_action_mask[action]:
            EnvLogger.warn_on_illegal_move()
            self._cumulative_rewards[self.agent_selection] = 0
            self.dones = {d: True for d in self.dones}
            self._prev_obs = None
            self.rewards = {d: 0 for d in self.dones}
            self.rewards[current_agent] = float(self._illegal_value)
            self._accumulate_rewards()
            self._dones_step_first()
            self._terminated = True
        else:
            super().step(action)


class CaptureStdoutWrapper(BaseWrapper):
    def __init__(self, env):
        super().__init__(env)
        self.metadata['render.modes'].append("ansi")

    def render(self, mode="human"):
        if mode == "human":
            super().render()
        elif mode == "ansi":
            with capture_stdout() as stdout:

                super().render()

                val = stdout.getvalue()
            return val


class AssertOutOfBoundsWrapper(BaseWrapper):
    '''
    this wrapper crashes for out of bounds actions
    Should be used for Discrete spaces
    '''
    def __init__(self, env):
        super().__init__(env)
        assert all(isinstance(space, Discrete) for space in self.action_spaces.values()), "should only use AssertOutOfBoundsWrapper for Discrete spaces"

    def step(self, action):
        assert (action is None and self.dones[self.agent_selection]) or self.action_spaces[self.agent_selection].contains(action), "action is not in action space"
        super().step(action)


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

            EnvLogger.warn_action_out_of_bound(action=action, action_space=space, backup_policy="clipping to space")
            action = np.clip(action, space.low, space.high)

        super().step(action)


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
        super().__init__(env)

    def __getattr__(self, value):
        '''
        raises an error message when data is gotten from the env
        which should only be gotten after reset
        '''
        if value == "agent_order":
            raise AttributeError("agent_order has been removed from the API. Please consider using agent_iter instead.")
        elif value in {"rewards", "dones", "infos", "agent_selection", "num_agents", "agents"}:
            raise AttributeError("{} cannot be accessed before reset".format(value))
        else:
            raise AttributeError("'{}' object has no attribute '{}'".format(type(self).__name__, value))

    def seed(self, seed=None):
        self._has_reset = False
        super().seed(seed)

    def render(self, mode='human'):
        if not self._has_reset:
            EnvLogger.error_render_before_reset()
        assert mode in self.metadata['render.modes']
        self._has_rendered = True
        return super().render(mode)

    def close(self):
        super().close()
        if not self._has_rendered:
            EnvLogger.warn_close_unrendered_env()
        if not self._has_reset:
            EnvLogger.warn_close_before_reset()

        self._has_rendered = False
        self._has_reset = False

    def step(self, action):
        if not self._has_reset:
            EnvLogger.error_step_before_reset()
        elif not self.agents:
            EnvLogger.warn_step_after_done()
            return None
        else:
            super().step(action)

    def observe(self, agent):
        if not self._has_reset:
            EnvLogger.error_observe_before_reset()
        return super().observe(agent)

    def reset(self):
        self._has_reset = True
        super().reset()
