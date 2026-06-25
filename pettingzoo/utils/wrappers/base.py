from __future__ import annotations

from typing import Any

import gymnasium.spaces
import numpy as np
from typing_extensions import override

from pettingzoo.utils.env import ActionType, AECEnv, AgentID, ObsType


class BaseWrapper(AECEnv[AgentID, ObsType, ActionType]):
    """Creates a wrapper around `env` parameter.

    All AECEnv wrappers should inherit from this base class
    """

    def __init__(self, env: AECEnv[AgentID, ObsType, ActionType]):
        super().__init__()
        self.env = env

    def __getattr__(self, name: str) -> Any:
        """Returns an attribute with ``name``, unless ``name`` starts with an underscore."""
        if name.startswith("_") and name != "_cumulative_rewards":
            raise AttributeError(f"accessing private attribute '{name}' is prohibited")
        return getattr(self.env, name)

    @property
    @override
    def unwrapped(self) -> AECEnv[AgentID, ObsType, ActionType]:
        return self.env.unwrapped

    @override
    def close(self) -> None:
        self.env.close()

    @override
    def render(self) -> None | np.ndarray | str | list[Any]:
        return self.env.render()

    @override
    def reset(self, seed: int | None = None, options: dict[str, Any] | None = None):
        self.env.reset(seed=seed, options=options)

    @override
    def observe(self, agent: AgentID) -> ObsType | None:
        return self.env.observe(agent)

    @override
    def state(self) -> np.ndarray:
        return self.env.state()

    @override
    def step(self, action: ActionType) -> None:
        self.env.step(action)

    @override
    def observation_space(self, agent: AgentID) -> gymnasium.spaces.Space[ObsType]:
        return self.env.observation_space(agent)

    @override
    def action_space(self, agent: AgentID) -> gymnasium.spaces.Space[ActionType]:
        return self.env.action_space(agent)

    @override
    def __str__(self) -> str:
        """Returns a name which looks like: "max_observation<space_invaders_v1>"."""
        return f"{type(self).__name__}<{str(self.env)}>"
