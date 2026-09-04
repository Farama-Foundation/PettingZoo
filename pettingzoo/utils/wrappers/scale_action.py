"""Wrappers that scale the bounds of a Box action space."""

from __future__ import annotations

from typing import Any, cast

import gymnasium.spaces
import numpy as np
from gymnasium.spaces import Box
from typing_extensions import override

from pettingzoo.utils.env import ActionType, AECEnv, AgentID, ObsType, ParallelEnv
from pettingzoo.utils.wrappers.base import BaseWrapper
from pettingzoo.utils.wrappers.base_parallel import BaseParallelWrapper


def _scaled_space(
    space: gymnasium.spaces.Space[Any], scale: float, wrapper_name: str
) -> Box:
    """Returns ``space`` with its bounds multiplied by ``scale``.

    A negative scale maps ``low`` above ``high``, so the two are swapped to keep the
    Box valid.
    """
    assert isinstance(space, Box), (
        f"{wrapper_name} only works with Box action spaces, got {type(space).__name__}."
    )
    low = space.low * scale
    high = space.high * scale
    if scale < 0:
        low, high = high, low
    dtype = cast(
        "type[np.floating[Any]] | type[np.integer[Any]]", np.dtype(space.dtype).type
    )
    return Box(low=low, high=high, shape=space.shape, dtype=dtype)


def _unscaled_action(
    action: np.ndarray, space: Box, scaled_space: Box, scale: float
) -> np.ndarray:
    """Maps an action from ``scaled_space`` back into ``space``.

    Multiplying a bound by ``scale`` and dividing it back is not exact in floating
    point, so an action sitting on a bound of the scaled space can come back a
    fraction outside ``space``. Those are clipped. An action that was already
    outside ``scaled_space`` is left alone, so wrappers further in still see it as
    out of bounds.
    """
    action = np.asarray(action)
    unscaled = (action / scale).astype(space.dtype)
    inside = (action >= scaled_space.low) & (action <= scaled_space.high)
    return np.where(inside, np.clip(unscaled, space.low, space.high), unscaled)


class ScaleActionV1(BaseWrapper[AgentID, ObsType, Any]):
    """Scales the bounds of each agent's Box action space by a constant factor.

    The action space this wrapper advertises has ``low`` and ``high`` multiplied by
    ``scale``. Actions are divided by ``scale`` before they reach the wrapped
    environment, so an action drawn from the advertised space is a valid action for
    the wrapped environment. Actions on a bound of the advertised space are clipped
    to the wrapped bound, since the round trip through ``scale`` is not exact in
    floating point. An action outside the advertised space is passed through as is.

    Scaling an integer Box narrows what can be reached: at ``scale`` 0.5, a
    ``Box(0, 10, dtype=int64)`` advertises ``Box(0, 5)`` and only even actions are
    reachable. A bound large enough that ``bound * scale`` overflows the dtype
    becomes infinite, and actions there stay infinite.

    :param env: The AEC environment to wrap.
    :param scale: Non-zero factor applied to the action space bounds. A negative
        scale flips the bounds, so they are swapped to keep the Box valid.
    """

    def __init__(self, env: AECEnv[AgentID, ObsType, ActionType], scale: float):
        assert isinstance(env, AECEnv), (
            "ScaleActionV1 is only compatible with AEC environments, "
            "use ScaleActionParallelV1 instead."
        )
        assert scale != 0, "ScaleActionV1 needs a non-zero scale."
        super().__init__(env)
        self.scale = scale
        self._action_spaces: dict[AgentID, Box] = {}
        for agent in getattr(env, "possible_agents", []):
            self.action_space(agent)

    @override
    def action_space(self, agent: AgentID) -> Box:
        if agent not in self._action_spaces:
            self._action_spaces[agent] = _scaled_space(
                self.env.action_space(agent), self.scale, "ScaleActionV1"
            )
        return self._action_spaces[agent]

    @override
    def step(self, action: np.ndarray | None) -> None:
        if action is not None:
            agent = self.agent_selection
            space = self.env.action_space(agent)
            assert isinstance(space, Box), (
                "ScaleActionV1 only works with Box action spaces."
            )
            action = _unscaled_action(
                action, space, self.action_space(agent), self.scale
            )
        self.env.step(action)

    @override
    def __str__(self) -> str:
        return f"ScaleActionV1<{self.env!s}>"


class ScaleActionParallelV1(BaseParallelWrapper[AgentID, ObsType, Any]):
    """Scales the bounds of each agent's Box action space by a constant factor.

    The action space this wrapper advertises has ``low`` and ``high`` multiplied by
    ``scale``. Actions are divided by ``scale`` before they reach the wrapped
    environment, so an action drawn from the advertised space is a valid action for
    the wrapped environment. Actions on a bound of the advertised space are clipped
    to the wrapped bound, since the round trip through ``scale`` is not exact in
    floating point. An action outside the advertised space is passed through as is.

    Scaling an integer Box narrows what can be reached: at ``scale`` 0.5, a
    ``Box(0, 10, dtype=int64)`` advertises ``Box(0, 5)`` and only even actions are
    reachable. A bound large enough that ``bound * scale`` overflows the dtype
    becomes infinite, and actions there stay infinite.

    :param env: The parallel environment to wrap.
    :param scale: Non-zero factor applied to the action space bounds. A negative
        scale flips the bounds, so they are swapped to keep the Box valid.
    """

    def __init__(self, env: ParallelEnv[AgentID, ObsType, ActionType], scale: float):
        assert scale != 0, "ScaleActionParallelV1 needs a non-zero scale."
        super().__init__(env)
        self.scale = scale
        self._action_spaces: dict[AgentID, Box] = {}
        for agent in getattr(env, "possible_agents", []):
            self.action_space(agent)

    @override
    def action_space(self, agent: AgentID) -> Box:
        if agent not in self._action_spaces:
            self._action_spaces[agent] = _scaled_space(
                self.env.action_space(agent), self.scale, "ScaleActionParallelV1"
            )
        return self._action_spaces[agent]

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
        unscaled = {}
        for agent, action in actions.items():
            space = self.env.action_space(agent)
            assert isinstance(space, Box), (
                "ScaleActionParallelV1 only works with Box action spaces."
            )
            unscaled[agent] = _unscaled_action(
                action, space, self.action_space(agent), self.scale
            )
        return self.env.step(unscaled)

    @override
    def __str__(self) -> str:
        return f"ScaleActionParallelV1<{self.env!s}>"
