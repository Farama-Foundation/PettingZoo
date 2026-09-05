from __future__ import annotations

import re
import warnings
from typing import Any, cast

import gymnasium.spaces
import numpy as np
from typing_extensions import override

from pettingzoo.utils.env import ActionType, AECEnv, AgentID, ObsType, ParallelEnv
from pettingzoo.utils.wrappers.base import BaseWrapper
from pettingzoo.utils.wrappers.base_parallel import BaseParallelWrapper


def _indicator_map(agents: list[AgentID], type_only: bool) -> dict[AgentID, int]:
    if not type_only:
        return {agent: index for index, agent in enumerate(agents)}

    assert all(
        isinstance(agent, str) and re.match(r"[a-z]+_[0-9]+", agent) for agent in agents
    ), "when type_only is True, agent names must follow the <type>_<n> format"
    type_indices: dict[str, int] = {}
    indicators: dict[AgentID, int] = {}
    for agent in agents:
        agent_type = cast("str", agent).split("_")[0]
        indicators[agent] = type_indices.setdefault(agent_type, len(type_indices))

    if len(type_indices) == 1:
        warnings.warn(
            "AgentIndicatorV1 is degenerate because the environment has only one agent type",
            stacklevel=2,
        )
    return indicators


def _validate_observation_spaces(
    spaces: list[gymnasium.spaces.Space[Any]],
) -> None:
    assert spaces and all(repr(space) == repr(spaces[0]) for space in spaces), (
        "observation spaces must be identical to add an agent indicator"
    )
    _change_observation_space(spaces[0], 1)


def _indicator_value(space: gymnasium.spaces.Box) -> Any:
    return 1.0 if np.isinf(space.high).any() else np.max(space.high)


def _change_observation_space(
    space: gymnasium.spaces.Space[Any], num_indicators: int
) -> gymnasium.spaces.Space[Any]:
    if isinstance(space, gymnasium.spaces.Discrete):
        return gymnasium.spaces.Discrete(space.n * num_indicators)

    assert isinstance(space, gymnasium.spaces.Box) and len(space.shape) in {1, 2, 3}, (
        f"AgentIndicatorV1 requires a 1D, 2D, or 3D Box or Discrete observation "
        f"space, received {space}"
    )

    low = space.low if len(space.shape) != 2 else np.expand_dims(space.low, axis=2)
    high = space.high if len(space.shape) != 2 else np.expand_dims(space.high, axis=2)
    indicator_value = _indicator_value(space)
    indicator_shape = (
        (num_indicators,)
        if len(space.shape) == 1
        else low.shape[:2] + (num_indicators,)
    )
    indicator_low = np.full(
        indicator_shape, min(0.0, indicator_value), dtype=space.dtype
    )
    indicator_high = np.full(
        indicator_shape, max(0.0, indicator_value), dtype=space.dtype
    )
    axis = 0 if len(space.shape) == 1 else 2
    return gymnasium.spaces.Box(
        low=np.concatenate((low, indicator_low), axis=axis),
        high=np.concatenate((high, indicator_high), axis=axis),
        dtype=cast("Any", space.dtype),
    )


def _change_observation(
    observation: Any,
    space: gymnasium.spaces.Space[Any],
    indicator: int,
    num_indicators: int,
) -> Any:
    if isinstance(space, gymnasium.spaces.Discrete):
        return (observation - space.start) * num_indicators + indicator

    assert isinstance(space, gymnasium.spaces.Box)
    if len(space.shape) == 1:
        transformed = np.pad(observation, (0, num_indicators))
        transformed[len(observation) + indicator] = _indicator_value(space)
        return transformed

    transformed = np.pad(
        observation if len(space.shape) == 3 else np.expand_dims(observation, axis=2),
        ((0, 0), (0, 0), (0, num_indicators)),
    )
    transformed[:, :, transformed.shape[2] - num_indicators + indicator] = (
        _indicator_value(space)
    )
    return transformed


class AgentIndicatorV1(BaseWrapper[AgentID, Any, ActionType]):
    """Adds an agent indicator to each observation.

    With ``type_only=True``, agents named ``<type>_<n>`` share an indicator for
    their type.

    :param env: The AEC environment to wrap.
    :param type_only: Whether to indicate agent types instead of individual agents.
    """

    def __init__(
        self,
        env: AECEnv[AgentID, ObsType, ActionType],
        type_only: bool = False,
    ):
        assert isinstance(env, AECEnv), (
            "AgentIndicatorV1 is only compatible with AEC environments, use "
            "AgentIndicatorParallelV1 instead"
        )
        super().__init__(env)
        self._indicators = _indicator_map(env.possible_agents, type_only)
        self._num_indicators = len(set(self._indicators.values()))
        spaces = [env.observation_space(agent) for agent in env.possible_agents]
        _validate_observation_spaces(spaces)
        self._observation_space = _change_observation_space(
            spaces[0], self._num_indicators
        )

    @override
    def observation_space(self, agent: AgentID) -> gymnasium.spaces.Space[Any]:
        return self._observation_space

    @override
    def observe(self, agent: AgentID) -> Any:
        observation = self.env.observe(agent)
        if observation is None:
            return None
        return _change_observation(
            observation,
            self.env.observation_space(agent),
            self._indicators[agent],
            self._num_indicators,
        )


class AgentIndicatorParallelV1(BaseParallelWrapper[AgentID, Any, ActionType]):
    """Adds an agent indicator to each observation.

    With ``type_only=True``, agents named ``<type>_<n>`` share an indicator for
    their type.

    :param env: The parallel environment to wrap.
    :param type_only: Whether to indicate agent types instead of individual agents.
    """

    def __init__(
        self,
        env: ParallelEnv[AgentID, ObsType, ActionType],
        type_only: bool = False,
    ):
        assert isinstance(env, ParallelEnv), (
            "AgentIndicatorParallelV1 is only compatible with parallel environments"
        )
        super().__init__(env)
        self._indicators = _indicator_map(env.possible_agents, type_only)
        self._num_indicators = len(set(self._indicators.values()))
        spaces = [env.observation_space(agent) for agent in env.possible_agents]
        _validate_observation_spaces(spaces)
        self._observation_space = _change_observation_space(
            spaces[0], self._num_indicators
        )

    @override
    def observation_space(self, agent: AgentID) -> gymnasium.spaces.Space[Any]:
        return self._observation_space

    def _transform(self, observations: dict[AgentID, ObsType]) -> dict[AgentID, Any]:
        return {
            agent: _change_observation(
                observation,
                self.env.observation_space(agent),
                self._indicators[agent],
                self._num_indicators,
            )
            for agent, observation in observations.items()
        }

    @override
    def reset(
        self, seed: int | None = None, options: dict[str, Any] | None = None
    ) -> tuple[dict[AgentID, Any], dict[AgentID, dict[str, Any]]]:
        observations, infos = self.env.reset(seed=seed, options=options)
        return self._transform(observations), infos

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
        return (
            self._transform(observations),
            rewards,
            terminations,
            truncations,
            infos,
        )
