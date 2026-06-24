from __future__ import annotations

from typing import Any

import numpy as np
from typing_extensions import override

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

    The following are raised:
    * AttributeError if any of the following are accessed before reset():
      rewards, terminations, truncations, infos, agent_selection,
      num_agents, agents.
    * An error if any of the following are called before reset:
      render(), step(), observe(), state(), agent_iter()
    * A warning if step() is called when there are no agents remaining.
    """

    def __init__(self, env: AECEnv[AgentID, ObsType, ActionType]):
        assert isinstance(
            env, AECEnv
        ), "OrderEnforcingWrapper is only compatible with AEC environments"
        self._has_reset = False
        self._has_updated = False
        super().__init__(env)

    @override
    def __getattr__(self, name: str) -> Any:
        """Raises an error if certain data is accessed before reset."""
        if (
            name
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
            raise AttributeError(f"{name} cannot be accessed before reset")
        return super().__getattr__(name)

    @override
    def render(self) -> None | np.ndarray | str | list[Any]:
        if not self._has_reset:
            EnvLogger.error_render_before_reset()
        return super().render()

    @override
    def step(self, action: ActionType) -> None:
        if not self._has_reset:
            EnvLogger.error_step_before_reset()
        elif not self.agents:
            self._has_updated = True
            EnvLogger.warn_step_after_terminated_truncated()
        else:
            self._has_updated = True
            super().step(action)

    @override
    def observe(self, agent: AgentID) -> ObsType | None:
        if not self._has_reset:
            EnvLogger.error_observe_before_reset()
        return super().observe(agent)

    @override
    def state(self) -> np.ndarray:
        if not self._has_reset:
            EnvLogger.error_state_before_reset()
        return super().state()

    @override
    def agent_iter(
        self, max_iter: int = 2**63
    ) -> AECOrderEnforcingIterable[AgentID, ObsType, ActionType]:
        if not self._has_reset:
            EnvLogger.error_agent_iter_before_reset()
        return AECOrderEnforcingIterable(self, max_iter)

    @override
    def reset(
        self, seed: int | None = None, options: dict[str, Any] | None = None
    ) -> None:
        self._has_reset = True
        self._has_updated = True
        super().reset(seed=seed, options=options)

    @override
    def __str__(self) -> str:
        if hasattr(self, "metadata"):
            return (
                str(self.env)
                if self.__class__ is OrderEnforcingWrapper
                else f"{type(self).__name__}<{str(self.env)}>"
            )
        return repr(self)


class AECOrderEnforcingIterable(AECIterable[AgentID, ObsType, ActionType]):
    @override
    def __iter__(self) -> AECOrderEnforcingIterator[AgentID, ObsType, ActionType]:
        return AECOrderEnforcingIterator(self.env, self.max_iter)


class AECOrderEnforcingIterator(AECIterator[AgentID, ObsType, ActionType]):
    def __init__(
        self, env: OrderEnforcingWrapper[AgentID, ObsType, ActionType], max_iter: int
    ):
        assert isinstance(
            env, OrderEnforcingWrapper
        ), "env must be wrapped by OrderEnforcingWrapper"
        super().__init__(env, max_iter)

    @override
    def __next__(self) -> AgentID:
        agent = super().__next__()
        assert (
            self.env._has_updated  # type: ignore
        ), "need to call step() or reset() in a loop over `agent_iter`"
        self.env._has_updated = False  # type: ignore
        return agent
