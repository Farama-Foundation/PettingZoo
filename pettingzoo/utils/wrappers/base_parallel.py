from __future__ import annotations

import warnings

import gymnasium.spaces
import numpy as np
from gymnasium.utils import seeding

from pettingzoo.utils.env import ActionType, ObsType, ParallelEnv


class BaseParallelWrapper(ParallelEnv):
    def __init__(self, env: ParallelEnv):
        self.env = env

        self.metadata = env.metadata
        try:
            self.possible_agents = env.possible_agents
        except AttributeError:
            pass

        # Not every environment has the .state_space attribute implemented
        try:
            self.state_space = (
                self.env.state_space  # pyright: ignore[reportGeneralTypeIssues]
            )
        except AttributeError:
            pass

    def reset(
        self, seed: int | None = None, options: dict | None = None
    ) -> tuple[dict[str, ObsType], dict[str, dict]]:
        self.np_random, _ = seeding.np_random(seed)

        res, info = self.env.reset(seed=seed, options=options)
        self.agents = self.env.agents
        return res, info

    def step(
        self, actions: dict[str, ActionType]
    ) -> tuple[
        dict[str, ObsType],
        dict[str, float],
        dict[str, bool],
        dict[str, bool],
        dict[str, dict],
    ]:
        res = self.env.step(actions)
        self.agents = self.env.agents
        return res

    def render(self) -> None | np.ndarray | str | list:
        return self.env.render()

    def close(self) -> None:
        return self.env.close()

    @property
    def unwrapped(self) -> ParallelEnv:
        return self.env.unwrapped

    def state(self) -> np.ndarray:
        return self.env.state()

    @property
    def observation_spaces(self) -> dict[str, gymnasium.spaces.Space]:
        warnings.warn(
            "The `observation_spaces` dictionary is deprecated. Use the `observation_space` function instead."
        )
        try:
            return {
                agent: self.observation_space(agent) for agent in self.possible_agents
            }
        except AttributeError as e:
            raise AttributeError(
                "The base environment does not have an `observation_spaces` dict attribute. Use the environments `observation_space` method instead"
            ) from e

    @property
    def action_spaces(self) -> dict[str, gymnasium.spaces.Space]:
        warnings.warn(
            "The `action_spaces` dictionary is deprecated. Use the `action_space` function instead."
        )
        try:
            return {agent: self.action_space(agent) for agent in self.possible_agents}
        except AttributeError as e:
            raise AttributeError(
                "The base environment does not have an action_spaces dict attribute. Use the environments `action_space` method instead"
            ) from e

    def observation_space(self, agent: str) -> gymnasium.spaces.Space:
        return self.env.observation_space(agent)

    def action_space(self, agent: str) -> gymnasium.spaces.Space:
        return self.env.action_space(agent)
