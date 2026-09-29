from __future__ import annotations

from typing import Any

import numpy as np
from gymnasium.spaces import Box
from typing_extensions import override

from pettingzoo.utils.env import AECEnv, AgentID, ObsType, ParallelEnv
from pettingzoo.utils.env_logger import EnvLogger
from pettingzoo.utils.wrappers.base import BaseWrapper
from pettingzoo.utils.wrappers.base_parallel import BaseParallelWrapper


class ClipOutOfBoundsWrapper(BaseWrapper[Any, Any, Any]):
    """Clips the input action to fit in the continuous action space (emitting a warning if it does so).

    Applied to continuous environments in pettingzoo.
    """

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
        if action is not None and not space.contains(action):
            if np.isnan(action).any():
                EnvLogger.error_nan_action()
            assert space.shape == action.shape, (
                f"action should have shape {space.shape}, has shape {action.shape}"
            )

            EnvLogger.warn_action_out_of_bound(
                action=action, action_space=space, backup_policy="clipping to space"
            )
            action = np.clip(
                action,
                space.low,
                space.high,
            )

        super().step(action)

    @override
    def __str__(self) -> str:
        return str(self.env)


class ClipOutOfBoundsParallelV1(BaseParallelWrapper[AgentID, ObsType, Any]):
    """Clips each agent's Box action to that agent's action-space bounds.

    In-range actions pass through unchanged. An out-of-range action is clipped
    elementwise and emits a warning; malformed shapes and NaNs are rejected.
    The action spaces themselves are unchanged. Unlike SuperSuit's
    ``clip_actions_v0``, this wrapper warns when clipping and rejects NaNs,
    matching :class:`ClipOutOfBoundsWrapper` for AEC environments.

    :param env: The parallel environment to wrap.
    """

    def __init__(self, env: ParallelEnv[AgentID, ObsType, Any]):
        assert isinstance(env, ParallelEnv), (
            "ClipOutOfBoundsParallelV1 is only compatible with parallel environments."
        )
        super().__init__(env)
        assert all(
            isinstance(self.action_space(agent), Box)
            for agent in getattr(self, "possible_agents", [])
        ), "should only use ClipOutOfBoundsParallelV1 for Box spaces"

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
                "should only use ClipOutOfBoundsParallelV1 for Box spaces"
            )
            if space.contains(action):
                clipped_actions[agent] = action
                continue

            action_array = np.asarray(action)
            if np.isnan(action_array).any():
                EnvLogger.error_nan_action()
            assert space.shape == action_array.shape, (
                f"action should have shape {space.shape}, has shape {action_array.shape}"
            )
            EnvLogger.warn_action_out_of_bound(
                action=action, action_space=space, backup_policy="clipping to space"
            )
            clipped_actions[agent] = np.clip(action_array, space.low, space.high)

        return self.env.step(clipped_actions)

    @override
    def __str__(self) -> str:
        return f"ClipOutOfBoundsParallelV1<{self.env!s}>"
