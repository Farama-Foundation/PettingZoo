from __future__ import annotations

from typing import Any

import numpy as np

from pettingzoo.utils.env import (
    ActionType,
    AECEnv,
    AECIterable,
    AECIterator,
    AgentID,
    ObsType,
)
from pettingzoo.utils.env_logger import EnvLogger
from pettingzoo.utils.wrappers.base import BaseWrapper


class OrderEnforcingWrapper(BaseWrapper[AgentID, ObsType, ActionType]):
    """Checks if function calls or attribute access are in a disallowed order.

    * error on getting rewards, terminations, truncations, infos, agent_selection before reset
    * error on calling step, observe before reset
    * error on iterating without stepping or resetting environment.
    * warn on calling close before render or reset
    * warn on calling step after environment is terminated or truncated
    """

    def __init__(self, env: AECEnv[AgentID, ObsType, ActionType]):
        assert isinstance(
            env, AECEnv
        ), "OrderEnforcingWrapper is only compatible with AEC environments"
        self._has_reset = False
        self._has_rendered = False
        self._has_updated = False
        super().__init__(env)

    def __getattr__(self, value: str) -> Any:
        """Raises an error message when data is gotten from the env.

        Should only be gotten after reset
        """
        if value == "unwrapped":
            return self.env.unwrapped
        elif value == "render_mode" and hasattr(self.env, "render_mode"):
            return self.env.render_mode  # pyright: ignore[reportGeneralTypeIssues]
        elif value == "possible_agents":
            try:
                return self.env.possible_agents
            except AttributeError:
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
        elif (
            value
            in {
                "rewards",
                "terminations",
                "truncations",
                "infos",
                "agent_selection",
                "num_agents",
                "agents",
            }
            and not self._has_reset
        ):
            raise AttributeError(f"{value} cannot be accessed before reset")
        else:
            return super().__getattr__(value)

    def render(self) -> None | np.ndarray | str | list:
        if not self._has_reset:
            EnvLogger.error_render_before_reset()
        self._has_rendered = True
        return super().render()

    def step(self, action: ActionType) -> None:
        if not self._has_reset:
            EnvLogger.error_step_before_reset()
        elif not self.agents:
            self._has_updated = True
            EnvLogger.warn_step_after_terminated_truncated()
            return None
        else:
            self._has_updated = True
            super().step(action)

    def observe(self, agent: AgentID) -> ObsType | None:
        if not self._has_reset:
            EnvLogger.error_observe_before_reset()
        return super().observe(agent)

    def state(self) -> np.ndarray:
        if not self._has_reset:
            EnvLogger.error_state_before_reset()
        return super().state()

    def agent_iter(
        self, max_iter: int = 2**63
    ) -> AECOrderEnforcingIterable[AgentID, ObsType, ActionType]:
        if not self._has_reset:
            EnvLogger.error_agent_iter_before_reset()
        return AECOrderEnforcingIterable(self, max_iter)

    def reset(self, seed: int | None = None, options: dict | None = None) -> None:
        self._has_reset = True
        self._has_updated = True
        super().reset(seed=seed, options=options)

    def __str__(self) -> str:
        if hasattr(self, "metadata"):
            return (
                str(self.env)
                if self.__class__ is OrderEnforcingWrapper
                else f"{type(self).__name__}<{str(self.env)}>"
            )
        else:
            return repr(self)


class AECOrderEnforcingIterable(AECIterable[AgentID, ObsType, ActionType]):
    def __iter__(self) -> AECOrderEnforcingIterator[AgentID, ObsType, ActionType]:
        return AECOrderEnforcingIterator(self.env, self.max_iter)


class AECOrderEnforcingIterator(AECIterator[AgentID, ObsType, ActionType]):
    def __next__(self) -> AgentID:
        agent = super().__next__()
        assert hasattr(
            self.env, "_has_updated"
        ), "env must be wrapped by OrderEnforcingWrapper"
        assert (
            self.env._has_updated  # pyright: ignore[reportGeneralTypeIssues]
        ), "need to call step() or reset() in a loop over `agent_iter`"
        self.env._has_updated = False  # pyright: ignore[reportGeneralTypeIssues]
        return agent
