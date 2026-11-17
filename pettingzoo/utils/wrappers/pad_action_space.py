"""Wrappers that pad every agent's action space up to a single shared space."""

from __future__ import annotations

from typing import Any

import numpy as np
from gymnasium.spaces import Box, Discrete, Space
from typing_extensions import override

from pettingzoo.utils.env import ActionType, AECEnv, AgentID, ObsType, ParallelEnv
from pettingzoo.utils.wrappers.base import BaseWrapper
from pettingzoo.utils.wrappers.base_parallel import BaseParallelWrapper
from pettingzoo.utils.wrappers.pad_observations import _check_paddable, _padded_space


def _unpad_action(space: Space[Any], action: Any) -> Any:
    """Maps an action from the shared space back into the agent's own ``space``."""
    if action is None:
        return None
    if isinstance(space, Discrete):
        # an action only another agent has maps to this agent's first action
        start = int(space.start)
        return action if start <= int(action) < start + int(space.n) else space.start
    assert isinstance(space, Box)
    return np.asarray(action)[tuple(slice(0, dim) for dim in space.shape)]


class PadActionSpaceV1(BaseWrapper[AgentID, ObsType, Any]):
    """Pads each agent's action space up to one shared action space.

    The shared space covers the action spaces of ``possible_agents``, built the same
    way as :class:`PadObservationsV1` builds its observation space: for Box spaces
    the largest size along each axis, for Discrete spaces the range covering all of
    them. Every agent then reports that same space.

    Before an action reaches the wrapped environment it is mapped back into the
    acting agent's own space: a Box action is sliced to the agent's original shape,
    and a Discrete action outside the agent's own range becomes its first action
    (``0`` for a space starting at zero). ``None`` actions of dead agents pass
    through.

    Box spaces have to agree on dtype and number of dimensions. Anything other than Box
    and Discrete, or a mix of both, is rejected.

    Ported from SuperSuit's pad_action_space_v0; the version suffix continues that
    numbering.

    :param env: The AEC environment to wrap.
    """

    def __init__(self, env: AECEnv[AgentID, ObsType, ActionType]):
        assert isinstance(env, AECEnv), (
            "PadActionSpaceV1 is only compatible with AEC environments, "
            "use PadActionSpaceParallelV1 instead."
        )
        assert hasattr(env, "possible_agents"), (
            "environment passed to PadActionSpaceV1 must have a possible_agents list."
        )
        super().__init__(env)
        spaces = [env.action_space(agent) for agent in env.possible_agents]
        _check_paddable(spaces, kind="action")
        self._action_space = _padded_space(spaces)

    @override
    def action_space(self, agent: AgentID) -> Space[Any]:
        return self._action_space

    @override
    def step(self, action: Any) -> None:
        space = self.env.action_space(self.agent_selection)
        self.env.step(_unpad_action(space, action))

    @override
    def __str__(self) -> str:
        return f"PadActionSpaceV1<{self.env!s}>"


class PadActionSpaceParallelV1(BaseParallelWrapper[AgentID, ObsType, Any]):
    """Pads each agent's action space up to one shared action space.

    The shared space covers the action spaces of ``possible_agents``, built the same
    way as :class:`PadObservationsParallelV1` builds its observation space: for Box
    spaces the largest size along each axis, for Discrete spaces the range covering
    all of them. Every agent then reports that same space.

    Before the actions reach the wrapped environment, each one is mapped back into
    its agent's own space: a Box action is sliced to the agent's original shape, and
    a Discrete action outside the agent's own range becomes its first action (``0``
    for a space starting at zero).

    Box spaces have to agree on dtype and number of dimensions. Anything other than Box
    and Discrete, or a mix of both, is rejected.

    Ported from SuperSuit's pad_action_space_v0; the version suffix continues that
    numbering.

    :param env: The parallel environment to wrap.
    """

    def __init__(self, env: ParallelEnv[AgentID, ObsType, ActionType]):
        assert isinstance(env, ParallelEnv), (
            "PadActionSpaceParallelV1 is only compatible with parallel environments, "
            "use PadActionSpaceV1 instead."
        )
        assert hasattr(env, "possible_agents"), (
            "environment passed to PadActionSpaceParallelV1 must have a "
            "possible_agents list."
        )
        super().__init__(env)
        spaces = [env.action_space(agent) for agent in env.possible_agents]
        _check_paddable(spaces, kind="action")
        self._action_space = _padded_space(spaces)

    @override
    def action_space(self, agent: AgentID) -> Space[Any]:
        return self._action_space

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
                agent: _unpad_action(self.env.action_space(agent), action)
                for agent, action in actions.items()
            }
        )

    @override
    def __str__(self) -> str:
        return f"PadActionSpaceParallelV1<{self.env!s}>"
