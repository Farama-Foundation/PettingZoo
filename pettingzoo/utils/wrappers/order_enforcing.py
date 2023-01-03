from ..env import AECIterable, AECIterator
from ..env_logger import EnvLogger
from .base import BaseWrapper


class OrderEnforcingWrapper(BaseWrapper):
    """Checks if function calls or attribute access are in a disallowed order.

    * error on getting rewards, terminations, truncations, infos, agent_selection before reset
    * error on calling step, observe before reset
    * error on iterating without stepping or resetting environment.
    * warn on calling close before render or reset
    * warn on calling step after environment is terminated or truncated
    """

    def __init__(self, env):
        self._has_reset = False
        self._has_rendered = False
        self._has_updated = False
        super().__init__(env)

    def __getattr__(self, value):
        """Raises an error message when data is gotten from the env.

        Should only be gotten after reset
        """
        if value == "unwrapped":
            return self.env.unwrapped
        elif value == "render_mode":
            return self.env.render_mode
        elif value == "possible_agents":
            EnvLogger.error_possible_agents_attribute_missing("possible_agents")
        elif value == "observation_spaces":
            raise AttributeError(
                "The base environment does not have an possible_agents attribute. Use the environments `observation_space` method instead"
            )
        elif value == "action_spaces":
            raise AttributeError(
                "The base environment does not have an possible_agents attribute. Use the environments `action_space` method instead"
            )
        elif value == "agent_order":
            raise AttributeError(
                "agent_order has been removed from the API. Please consider using agent_iter instead."
            )
        elif value in {
            "rewards",
            "terminations",
            "truncations",
            "infos",
            "agent_selection",
            "num_agents",
            "agents",
        }:
            raise AttributeError(f"{value} cannot be accessed before reset")
        else:
            raise AttributeError(
                f"'{type(self).__name__}' object has no attribute '{value}'"
            )

    def render(self):
        if not self._has_reset:
            EnvLogger.error_render_before_reset()
        self._has_rendered = True
        return super().render()

    def step(self, action):
        if not self._has_reset:
            EnvLogger.error_step_before_reset()
        elif not self.agents:
            self._has_updated = True
            EnvLogger.warn_step_after_terminated_truncated()
            return None
        else:
            self._has_updated = True
            super().step(action)

    def observe(self, agent):
        if not self._has_reset:
            EnvLogger.error_observe_before_reset()
        return super().observe(agent)

    def state(self):
        if not self._has_reset:
            EnvLogger.error_state_before_reset()
        return super().state()

    def agent_iter(self, max_iter=2**63):
        if not self._has_reset:
            EnvLogger.error_agent_iter_before_reset()
        return AECOrderEnforcingIterable(self, max_iter)

    def reset(self, seed=None, return_info=False, options=None):
        self._has_reset = True
        self._has_updated = True
        super().reset(seed=seed, options=options)

    def __str__(self):
        if hasattr(self, "metadata"):
            return (
                str(self.env)
                if self.__class__ is OrderEnforcingWrapper
                else f"{type(self).__name__}<{str(self.env)}>"
            )
        else:
            return repr(self)


class AECOrderEnforcingIterable(AECIterable):
    def __iter__(self):
        return AECOrderEnforcingIterator(self.env, self.max_iter)


class AECOrderEnforcingIterator(AECIterator):
    def __next__(self):
        agent = super().__next__()
        assert (
            self.env._has_updated
        ), "need to call step() or reset() in a loop over `agent_iter`"
        self.env._has_updated = False
        return agent
