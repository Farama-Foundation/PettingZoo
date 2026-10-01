from __future__ import annotations

from typing import Any, overload

import numpy as np
from gymnasium.spaces import Box
from typing_extensions import override

from pettingzoo.utils.env import AECEnv, AgentID, ObsType, ParallelEnv
from pettingzoo.utils.env_logger import EnvLogger
from pettingzoo.utils.wrappers.base import BaseWrapper
from pettingzoo.utils.wrappers.base_parallel import BaseParallelWrapper


class ClipOutOfBoundsWrapper(BaseWrapper[Any, Any, Any]):
    """Clips the input action to fit in the continuous action space (emitting a warning if it does so).

    Supports both AEC and Parallel environments with Box action spaces. For AEC
    environments, ``step`` takes a single action (or ``None`` for a dead agent).
    For Parallel environments, ``step`` takes an action dictionary and clips each
    agent's action to that agent's bounds. In-range actions pass through unchanged;
    NaNs and malformed shapes are rejected. The action spaces are unchanged.
    """

    @overload
    def __new__(
        cls, env: AECEnv[Any, Any, Any] | None = None
    ) -> ClipOutOfBoundsWrapper: ...

    @overload
    def __new__(
        cls, env: ParallelEnv[AgentID, ObsType, Any]
    ) -> _ClipOutOfBoundsParallelWrapper[AgentID, ObsType]: ...

    def __new__(
        cls, env: AECEnv[Any, Any, Any] | ParallelEnv[Any, Any, Any] | None = None
    ) -> ClipOutOfBoundsWrapper | _ClipOutOfBoundsParallelWrapper[Any, Any]:
        if isinstance(env, ParallelEnv):
            return _ClipOutOfBoundsParallelWrapper(env)
        return super().__new__(cls)

    def __init__(self, env: AECEnv[Any, Any, Any]):
        super().__init__(env)
        assert isinstance(env, AECEnv), (
            "ClipOutOfBoundsWrapper is only compatible with AEC environments."
        )
        assert all(
            isinstance(self.action_space(agent), Box)
            for agent in getattr(self, "possible_agents", [])
        ), "should only use ClipOutOfBoundsWrapper for Box spaces"

    @override
    def step(self, action: np.ndarray | None) -> None:
        space = self.action_space(self.agent_selection)
        assert isinstance(space, Box), (
            "should only use ClipOutOfBoundsWrapper for Box spaces"
        )
        if action is not None:
            action = _clip_action(action, space)

        super().step(action)

    @override
    def __str__(self) -> str:
        return str(self.env)


class _ClipOutOfBoundsParallelWrapper(BaseParallelWrapper[AgentID, ObsType, Any]):
    """Parallel implementation selected by :class:`ClipOutOfBoundsWrapper`."""

    def __init__(self, env: ParallelEnv[AgentID, ObsType, Any]):
        super().__init__(env)
        assert all(
            isinstance(self.action_space(agent), Box)
            for agent in getattr(self, "possible_agents", [])
        ), "should only use ClipOutOfBoundsWrapper for Box spaces"

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
        clipped_actions = {}
        for agent, action in actions.items():
            space = self.action_space(agent)
            assert isinstance(space, Box), (
                "should only use ClipOutOfBoundsWrapper for Box spaces"
            )
            clipped_actions[agent] = _clip_action(action, space)

        return self.env.step(clipped_actions)

    @override
    def __str__(self) -> str:
        return str(self.env)


def _clip_action(action: Any, space: Box) -> Any:
    if space.contains(action):
        return action
    action_array = np.asarray(action)
    if np.isnan(action_array).any():
        EnvLogger.error_nan_action()
    assert space.shape == action_array.shape, (
        f"action should have shape {space.shape}, has shape {action_array.shape}"
    )
    EnvLogger.warn_action_out_of_bound(
        action=action, action_space=space, backup_policy="clipping to space"
    )
    return np.clip(action_array, space.low, space.high)
