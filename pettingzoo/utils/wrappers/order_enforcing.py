from .base import BaseWrapper
from ..env_logger import EnvLogger


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

    def agent_iter(self, max_iter=2**63):
        if not self._has_reset:
            EnvLogger.error_agent_iter_before_reset()
        return super().agent_iter(max_iter)

    def reset(self):
        self._has_reset = True
        super().reset()

    def __str__(self):
        if hasattr(self, 'metadata'):
            return str(self.env) if self.__class__ is OrderEnforcingWrapper else '{}<{}>'.format(type(self).__name__, str(self.env))
        else:
            return repr(self)
