from __future__ import annotations

from typing import Any

import gymnasium.spaces
from gymnasium.spaces.utils import flatten, flatten_space
from typing_extensions import override

from pettingzoo.utils.env import ActionType, AECEnv, AgentID, ObsType, ParallelEnv
from pettingzoo.utils.wrappers.base import BaseWrapper
from pettingzoo.utils.wrappers.base_parallel import BaseParallelWrapper


class FlattenObservation(BaseWrapper[AgentID, Any, ActionType]):
    """Flattens each agent's observation into a 1D array.

    :param env: The AEC environment to wrap.
    """

    def __init__(self, env: AECEnv[AgentID, ObsType, ActionType]):
        assert isinstance(env, AECEnv), (
            "FlattenObservation is only compatible with AEC environments, "
            "use FlattenObservationParallel instead."
        )
        super().__init__(env)
        self._obs_spaces: dict[AgentID, gymnasium.spaces.Space[Any]] = {}

    @override
    def observation_space(self, agent: AgentID) -> gymnasium.spaces.Space[Any]:
        if agent not in self._obs_spaces:
            self._obs_spaces[agent] = flatten_space(self.env.observation_space(agent))
        return self._obs_spaces[agent]

    @override
    def observe(self, agent: AgentID) -> Any:
        obs = self.env.observe(agent)
        if obs is None:
            return None
        return flatten(self.env.observation_space(agent), obs)

    @override
    def __str__(self) -> str:
        return f"FlattenObservation<{self.env!s}>"


class FlattenObservationParallel(BaseParallelWrapper[AgentID, Any, ActionType]):
    """Flattens each agent's observation into a 1D array.

    :param env: The parallel environment to wrap.
    """

    def __init__(self, env: ParallelEnv[AgentID, ObsType, ActionType]):
        super().__init__(env)
        self._obs_spaces: dict[AgentID, gymnasium.spaces.Space[Any]] = {}

    @override
    def observation_space(self, agent: AgentID) -> gymnasium.spaces.Space[Any]:
        if agent not in self._obs_spaces:
            self._obs_spaces[agent] = flatten_space(self.env.observation_space(agent))
        return self._obs_spaces[agent]

    def _flatten(self, observations: dict[AgentID, Any]) -> dict[AgentID, Any]:
        return {
            agent: flatten(self.env.observation_space(agent), obs)
            for agent, obs in observations.items()
        }

    @override
    def reset(
        self, seed: int | None = None, options: dict[str, Any] | None = None
    ) -> tuple[dict[AgentID, Any], dict[AgentID, dict[str, Any]]]:
        observations, infos = self.env.reset(seed=seed, options=options)
        return self._flatten(observations), infos

    @override
    def step(
        self, actions: dict[AgentID, ActionType]
    ) -> tuple[
        dict[AgentID, Any],
        dict[AgentID, float],
        dict[AgentID, bool],
        dict[AgentID, bool],
        dict[AgentID, dict[str, Any]],
    ]:
        observations, rewards, terminations, truncations, infos = self.env.step(actions)
        return self._flatten(observations), rewards, terminations, truncations, infos

    @override
    def __str__(self) -> str:
        return f"FlattenObservationParallel<{self.env!s}>"
