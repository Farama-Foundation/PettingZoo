from __future__ import annotations

import warnings

import gymnasium.spaces
import numpy as np
from gymnasium.utils import seeding

from pettingzoo.utils.env import ActionType, AgentID, ObsType, ParallelEnv


class BaseParallelWrapper(ParallelEnv[AgentID, ObsType, ActionType]):
    def __init__(self, env: ParallelEnv[AgentID, ObsType, ActionType]):
        self.env = env

    def reset(
        self, seed: int | None = None, options: dict | None = None
    ) -> tuple[dict[AgentID, ObsType], dict[AgentID, dict]]:
        return self.env.reset(seed=seed, options=options)

    def step(
        self, actions: dict[AgentID, ActionType]
    ) -> tuple[
        dict[AgentID, ObsType],
        dict[AgentID, float],
        dict[AgentID, bool],
        dict[AgentID, bool],
        dict[AgentID, dict],
    ]:
        return self.env.step(actions)

    def render(self) -> None | np.ndarray | str | list:
        return self.env.render()

    def close(self) -> None:
        return self.env.close()

    @property
    def unwrapped(self) -> ParallelEnv:
        return self.env.unwrapped

    def state(self) -> np.ndarray:
        return self.env.state()

    def observation_space(self, agent: AgentID) -> gymnasium.spaces.Space:
        return self.env.observation_space(agent)

    def action_space(self, agent: AgentID) -> gymnasium.spaces.Space:
        return self.env.action_space(agent)
