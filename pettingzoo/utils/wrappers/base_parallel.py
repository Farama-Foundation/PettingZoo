from __future__ import annotations

from typing import Any

import gymnasium.spaces
import numpy as np
from typing_extensions import override

from pettingzoo.utils.env import ActionType, AgentID, ObsType, ParallelEnv


class BaseParallelWrapper(ParallelEnv[AgentID, ObsType, ActionType]):
    def __init__(self, env: ParallelEnv[AgentID, ObsType, ActionType]):
        super().__init__()
        self.env = env

    def __getattr__(self, name: str):
        """Returns an attribute with ``name``, unless ``name`` starts with an underscore."""
        if name.startswith("_"):
            raise AttributeError(f"accessing private attribute '{name}' is prohibited")
        return getattr(self.env, name)

    @override
    def reset(
        self, seed: int | None = None, options: dict[str, Any] | None = None
    ) -> tuple[dict[AgentID, ObsType], dict[AgentID, dict[str, Any]]]:
        return self.env.reset(seed=seed, options=options)

    @override
    def step(
        self, actions: dict[AgentID, ActionType]
    ) -> tuple[
        dict[AgentID, ObsType],
        dict[AgentID, float],
        dict[AgentID, bool],
        dict[AgentID, bool],
        dict[AgentID, dict[str, Any]],
    ]:
        return self.env.step(actions)

    @override
    def render(self) -> None | np.ndarray | str | list[Any]:
        return self.env.render()

    @override
    def close(self) -> None:
        return self.env.close()

    @property
    @override
    def unwrapped(self) -> ParallelEnv[AgentID, ObsType, ActionType]:
        return self.env.unwrapped

    @override
    def state(self) -> np.ndarray:
        return self.env.state()

    @override
    def observation_space(self, agent: AgentID) -> gymnasium.spaces.Space:
        return self.env.observation_space(agent)

    @override
    def action_space(self, agent: AgentID) -> gymnasium.spaces.Space:
        return self.env.action_space(agent)
