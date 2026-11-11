from __future__ import annotations

from typing import Any

import gymnasium.spaces
import numpy as np
from gymnasium.spaces import Box
from typing_extensions import override

from pettingzoo.utils.env import ActionType, AECEnv, AgentID, ObsType, ParallelEnv
from pettingzoo.utils.wrappers.base import BaseWrapper
from pettingzoo.utils.wrappers.base_parallel import BaseParallelWrapper


def _cast_space(
    space: gymnasium.spaces.Space[Any],
    dtype: np.dtype[Any],
    agent: AgentID,
    wrapper: str,
) -> Box:
    """Returns ``space`` with its bounds and dtype cast to ``dtype``."""
    assert isinstance(space, Box), (
        f"{wrapper} only supports Box observation spaces, "
        f"agent {agent!r} has a {type(space).__name__}."
    )
    try:
        return Box(
            low=space.low.astype(dtype),
            high=space.high.astype(dtype),
            dtype=dtype.type,
        )
    except ValueError as e:
        raise ValueError(
            f"{wrapper} cannot cast agent {agent!r}'s observation space "
            f"{space} to {dtype}: the cast bounds are not a valid Box."
        ) from e


def _cached_space(
    space: gymnasium.spaces.Space[Any],
    dtype: np.dtype[Any],
    agent: AgentID,
    wrapper: str,
    spaces: dict[AgentID, Box],
    base_spaces: dict[AgentID, gymnasium.spaces.Space[Any]],
) -> Box:
    """Returns a cast space, retaining seeded state for equivalent replacements."""
    if base_spaces.get(agent) is not space:
        converted = _cast_space(space, dtype, agent, wrapper)
        cached = spaces.get(agent)
        # Equivalent replacements can occur after unpickling cached source spaces.
        # Retain the converted space's identity and seeded sampling state.
        if (
            cached is not None
            and cached.dtype == converted.dtype
            and cached.shape == converted.shape
            and np.array_equal(cached.low, converted.low)
            and np.array_equal(cached.high, converted.high)
        ):
            converted = cached
        spaces[agent] = converted
        base_spaces[agent] = space
    return spaces[agent]


class DtypeObservationV1(BaseWrapper[AgentID, Any, ActionType]):
    """Recasts each agent's observation to ``dtype``.

    The observation space becomes a Box with the same shape and the new dtype,
    with the old bounds put through the same cast. Every space in
    ``possible_agents`` is built and checked when the wrapper is created.

    Bounds that do not fit the new dtype wrap around, and casting an infinite
    bound to an integer dtype is undefined in numpy, so an unbounded Box cast to
    an integer dtype collapses to a single point that will not contain the
    observations. Both match SuperSuit's ``dtype_v0``.

    :param env: The AEC environment to wrap.
    :param dtype: Anything ``numpy.dtype`` accepts, e.g. ``np.float32``.
    """

    def __init__(self, env: AECEnv[AgentID, ObsType, ActionType], dtype: Any):
        assert isinstance(env, AECEnv), (
            "DtypeObservationV1 is only compatible with AEC environments, "
            "use DtypeObservationParallelV1 instead."
        )
        super().__init__(env)
        self.dtype = np.dtype(dtype)
        self._obs_spaces: dict[AgentID, Box] = {}
        self._base_obs_spaces: dict[AgentID, gymnasium.spaces.Space[Any]] = {}
        for agent in getattr(env, "possible_agents", []):
            _cached_space(
                env.observation_space(agent),
                self.dtype,
                agent,
                type(self).__name__,
                self._obs_spaces,
                self._base_obs_spaces,
            )

    @override
    def observation_space(self, agent: AgentID) -> Box:
        # Older pickles contain only the converted-space cache.
        return _cached_space(
            self.env.observation_space(agent),
            self.dtype,
            agent,
            type(self).__name__,
            self._obs_spaces,
            self.__dict__.setdefault("_base_obs_spaces", {}),
        )

    @override
    def observe(self, agent: AgentID) -> Any:
        obs = self.env.observe(agent)
        if obs is None:
            return None
        return np.asarray(obs).astype(self.dtype)

    @override
    def __str__(self) -> str:
        return f"DtypeObservationV1<{self.env!s}>"


class DtypeObservationParallelV1(BaseParallelWrapper[AgentID, Any, ActionType]):
    """Recasts each agent's observation to ``dtype``.

    The observation space becomes a Box with the same shape and the new dtype,
    with the old bounds put through the same cast. Every space in
    ``possible_agents`` is built and checked when the wrapper is created.

    Bounds that do not fit the new dtype wrap around, and casting an infinite
    bound to an integer dtype is undefined in numpy, so an unbounded Box cast to
    an integer dtype collapses to a single point that will not contain the
    observations. Both match SuperSuit's ``dtype_v0``.

    :param env: The parallel environment to wrap.
    :param dtype: Anything ``numpy.dtype`` accepts, e.g. ``np.float32``.
    """

    def __init__(self, env: ParallelEnv[AgentID, ObsType, ActionType], dtype: Any):
        super().__init__(env)
        self.dtype = np.dtype(dtype)
        self._obs_spaces: dict[AgentID, Box] = {}
        self._base_obs_spaces: dict[AgentID, gymnasium.spaces.Space[Any]] = {}
        for agent in getattr(env, "possible_agents", []):
            _cached_space(
                env.observation_space(agent),
                self.dtype,
                agent,
                type(self).__name__,
                self._obs_spaces,
                self._base_obs_spaces,
            )

    @override
    def observation_space(self, agent: AgentID) -> Box:
        return _cached_space(
            self.env.observation_space(agent),
            self.dtype,
            agent,
            type(self).__name__,
            self._obs_spaces,
            self.__dict__.setdefault("_base_obs_spaces", {}),
        )

    def _cast(self, observations: dict[AgentID, Any]) -> dict[AgentID, Any]:
        return {
            agent: np.asarray(obs).astype(self.dtype)
            for agent, obs in observations.items()
        }

    @override
    def reset(
        self, seed: int | None = None, options: dict[str, Any] | None = None
    ) -> tuple[dict[AgentID, Any], dict[AgentID, dict[str, Any]]]:
        observations, infos = self.env.reset(seed=seed, options=options)
        return self._cast(observations), infos

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
        return self._cast(observations), rewards, terminations, truncations, infos

    @override
    def __str__(self) -> str:
        return f"DtypeObservationParallelV1<{self.env!s}>"
