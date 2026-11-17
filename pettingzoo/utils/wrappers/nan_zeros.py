"""Wrappers that replace NaN actions with the all-zeros action."""

from __future__ import annotations

import warnings
from typing import Any

import gymnasium.spaces
import numpy as np
from gymnasium.spaces import Box
from typing_extensions import override

from pettingzoo.utils.env import ActionType, AECEnv, AgentID, ObsType, ParallelEnv
from pettingzoo.utils.wrappers.base import BaseWrapper
from pettingzoo.utils.wrappers.base_parallel import BaseParallelWrapper


def _check_space(space: gymnasium.spaces.Space[Any], wrapper_name: str) -> Box:
    """Returns ``space`` if the all-zeros action is valid in it, else raises.

    Only a floating-point ``Box`` can receive a NaN action, and zero has to lie
    within its bounds, or the replacement would itself be out of the space.
    """
    if not isinstance(space, Box) or not np.issubdtype(space.dtype, np.floating):
        raise TypeError(
            f"{wrapper_name} only works with floating-point Box action spaces, "
            f"got {space}."
        )
    if not (np.all(space.low <= 0) and np.all(space.high >= 0)):
        raise ValueError(
            f"{wrapper_name} replaces NaN actions with zeros, but zero is outside "
            f"the action space {space}."
        )
    return space


def _replace_nan(action: Any, space: Box, env: Any) -> Any:
    """Returns the all-zeros action of ``space`` if ``action`` contains a NaN."""
    if action is None or not np.isnan(action).any():
        return action
    warnings.warn(
        f"Step received a NaN action {action}. Environment is {env}. "
        "Taking the all-zeros action.",
        stacklevel=3,
    )
    return np.zeros(space.shape, dtype=space.dtype)


class NanZerosV1(BaseWrapper[AgentID, ObsType, Any]):
    """Replaces an action containing a NaN with the all-zeros action.

    The replacement has the shape and dtype of the agent's action space, and a
    warning is emitted whenever it happens. Actions without a NaN, and the
    ``None`` action of a dead agent, are passed through unchanged. The advertised
    action spaces are not modified.

    Only floating-point ``Box`` action spaces whose bounds contain zero are
    supported; any other action space raises an error rather than silently
    receiving an out-of-space replacement.

    :param env: The AEC environment to wrap.
    """

    def __init__(self, env: AECEnv[AgentID, ObsType, ActionType]):
        assert isinstance(env, AECEnv), (
            "NanZerosV1 is only compatible with AEC environments, "
            "use NanZerosParallelV1 instead."
        )
        super().__init__(env)
        for agent in getattr(env, "possible_agents", []):
            _check_space(self.env.action_space(agent), "NanZerosV1")

    @override
    def step(self, action: Any) -> None:
        space = _check_space(self.env.action_space(self.agent_selection), "NanZerosV1")
        self.env.step(_replace_nan(action, space, self))

    @override
    def __str__(self) -> str:
        return f"NanZerosV1<{self.env!s}>"


class NanZerosParallelV1(BaseParallelWrapper[AgentID, ObsType, Any]):
    """Replaces an action containing a NaN with the all-zeros action.

    Each agent's action is checked separately, so only the agents that sent a NaN
    receive the replacement. The replacement has the shape and dtype of the agent's
    action space, and a warning is emitted whenever it happens. The advertised
    action spaces are not modified.

    Only floating-point ``Box`` action spaces whose bounds contain zero are
    supported; any other action space raises an error rather than silently
    receiving an out-of-space replacement.

    :param env: The parallel environment to wrap.
    """

    def __init__(self, env: ParallelEnv[AgentID, ObsType, ActionType]):
        super().__init__(env)
        for agent in getattr(env, "possible_agents", []):
            _check_space(self.env.action_space(agent), "NanZerosParallelV1")

    @override
    def step(
        self, actions: dict[AgentID, Any]
    ) -> tuple[
        dict[AgentID, ObsType],
        dict[AgentID, float],
        dict[AgentID, bool],
        dict[AgentID, bool],
        dict[AgentID, dict[str, Any]],
    ]:
        replaced = {
            agent: _replace_nan(
                action,
                _check_space(self.env.action_space(agent), "NanZerosParallelV1"),
                self,
            )
            for agent, action in actions.items()
        }
        return self.env.step(replaced)

    @override
    def __str__(self) -> str:
        return f"NanZerosParallelV1<{self.env!s}>"
