"""Wrappers that replace NaN actions with a caller-supplied no-op action."""

from __future__ import annotations

import copy
import warnings
from typing import Any

import gymnasium.spaces
import numpy as np
from typing_extensions import override

from pettingzoo.utils.env import ActionType, AECEnv, AgentID, ObsType, ParallelEnv
from pettingzoo.utils.wrappers.base import BaseWrapper
from pettingzoo.utils.wrappers.base_parallel import BaseParallelWrapper


def _check_noop(
    space: gymnasium.spaces.Space[Any], no_op_action: Any, agent: Any
) -> None:
    if not space.contains(no_op_action):
        raise ValueError(
            f"The no-op action {no_op_action!r} is outside the action space "
            f"for agent {agent!r}: {space}."
        )


def _replace_nan(action: Any, no_op_action: Any, agent: Any, env: Any) -> Any:
    if action is None or not np.isnan(action).any():
        return action
    # Also validate at replacement time for environments with dynamic agents.
    _check_noop(env.action_space(agent), no_op_action, agent)
    warnings.warn(
        f"Step received a NaN action {action} for agent {agent!r}. "
        "Taking the supplied no-op action.",
        stacklevel=3,
    )
    # A mutable replacement must not be shared between agents or steps.
    return copy.deepcopy(no_op_action)


class NanNoopV1(BaseWrapper[AgentID, ObsType, Any]):
    """Replaces a numeric action containing a NaN with a supplied no-op action.

    A warning is emitted for each replacement. Numeric scalars and arrays are
    supported. Actions without NaNs, and ``None`` actions for dead agents, pass
    through unchanged. The advertised action spaces are not modified.

    The same caller-supplied no-op value is used for every agent. It must belong
    to each agent's action space, including its shape and dtype, or a ``ValueError``
    is raised. Known agents are checked at construction and the affected agent is
    checked on each replacement. Each replacement receives a copy of the value.

    :param env: The AEC environment to wrap.
    :param no_op_action: The no-op action, valid for all affected agents.
    """

    def __init__(
        self, env: AECEnv[AgentID, ObsType, ActionType], no_op_action: ActionType
    ):
        assert isinstance(env, AECEnv), (
            "NanNoopV1 is only compatible with AEC environments, "
            "use NanNoopParallelV1 instead."
        )
        super().__init__(env)
        self.no_op_action = copy.deepcopy(no_op_action)
        for agent in getattr(env, "possible_agents", []):
            _check_noop(env.action_space(agent), self.no_op_action, agent)

    @override
    def step(self, action: Any) -> None:
        self.env.step(
            _replace_nan(action, self.no_op_action, self.agent_selection, self.env)
        )

    @override
    def __str__(self) -> str:
        return f"NanNoopV1<{self.env!s}>"


class NanNoopParallelV1(BaseParallelWrapper[AgentID, ObsType, Any]):
    """Replaces each numeric action containing a NaN with a supplied no-op action.

    Each supplied action is checked independently and a warning is emitted for
    each replacement. Numeric scalars and arrays are supported. Actions without
    NaNs pass through unchanged, and the input dictionary is not modified.

    As in :class:`NanNoopV1`, the same caller-supplied no-op value must be valid
    in every affected agent's action space. Known agents are checked at
    construction and the affected agent is checked on each replacement. Each
    replacement receives a copy. The advertised action spaces are not modified.

    :param env: The parallel environment to wrap.
    :param no_op_action: The no-op action, valid for all affected agents.
    """

    def __init__(
        self, env: ParallelEnv[AgentID, ObsType, ActionType], no_op_action: ActionType
    ):
        super().__init__(env)
        self.no_op_action = copy.deepcopy(no_op_action)
        for agent in getattr(env, "possible_agents", []):
            _check_noop(env.action_space(agent), self.no_op_action, agent)

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
        return self.env.step(
            {
                agent: _replace_nan(action, self.no_op_action, agent, self.env)
                for agent, action in actions.items()
            }
        )

    @override
    def __str__(self) -> str:
        return f"NanNoopParallelV1<{self.env!s}>"
