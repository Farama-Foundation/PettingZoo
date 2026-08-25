"""Wrappers that pad every agent's observation up to a single shared space."""

from __future__ import annotations

from typing import Any, cast

import numpy as np
from gymnasium.spaces import Box, Discrete, Space
from typing_extensions import override

from pettingzoo.utils.env import ActionType, AECEnv, AgentID, ObsType, ParallelEnv
from pettingzoo.utils.wrappers.base import BaseWrapper
from pettingzoo.utils.wrappers.base_parallel import BaseParallelWrapper


def _check_paddable(spaces: list[Space[Any]]) -> None:
    """Checks that a list of observation spaces can be padded to a common space."""
    assert len(spaces) > 0, "environment must have at least one possible agent"
    first = spaces[0]
    assert isinstance(first, (Box, Discrete)), (
        "padding only supports Box and Discrete observation spaces, "
        f"got {type(first).__name__}"
    )

    expected = Box if isinstance(first, Box) else Discrete
    for space in spaces:
        assert isinstance(space, expected), (
            "all observation spaces must be either Box or Discrete, not a mix"
        )

    if isinstance(first, Box):
        for space in spaces:
            assert isinstance(space, Box)
            assert len(first.shape) == len(space.shape), (
                "all Box observation spaces must have the same number of dimensions"
            )
            assert first.dtype == space.dtype, (
                "all Box observation spaces must have the same dtype"
            )


def _pad_to(array: np.ndarray, shape: tuple[int, ...], value: Any) -> np.ndarray:
    """Pads ``array`` up to ``shape`` at the end of every axis."""
    if array.shape == shape:
        return array
    pad_widths = [(0, new - old) for new, old in zip(shape, array.shape)]
    return np.pad(array, pad_widths, constant_values=value)


def _padded_space(spaces: list[Space[Any]]) -> Space[Any]:
    """Builds the space every agent is padded up to."""
    if isinstance(spaces[0], Discrete):
        discretes = cast("list[Discrete[Any]]", spaces)
        start = min(int(space.start) for space in discretes)
        end = max(int(space.start) + int(space.n) for space in discretes)
        return Discrete(end - start, start=start)

    boxes = cast("list[Box]", spaces)
    shape = tuple(int(dim) for dim in np.max([box.shape for box in boxes], axis=0))
    # the fill values are what SuperSuit uses: a bound wide enough that padding an
    # agent's own bounds can never tighten the shared space
    lows = np.stack(
        [_pad_to(box.low, shape, np.minimum(0, np.min(box.low))) for box in boxes]
    )
    highs = np.stack(
        [_pad_to(box.high, shape, np.maximum(1e-5, np.max(box.high))) for box in boxes]
    )
    # every space has the same dtype, and padding keeps it
    return Box(
        low=np.min(lows, axis=0), high=np.max(highs, axis=0), dtype=lows.dtype.type
    )


def _pad_observation(space: Space[Any], obs: Any) -> Any:
    """Pads a single observation up to ``space``."""
    if obs is None:
        return None
    if not isinstance(space, Box):
        # Discrete observations already fit the shared space. SuperSuit returns the
        # space here instead of the observation, which is a bug.
        return obs
    return _pad_to(np.asarray(obs), space.shape, 0)


class PadObservations(BaseWrapper[AgentID, Any, ActionType]):
    """Pads each agent's observation up to one shared observation space.

    The shared space covers the observation spaces of ``possible_agents``. For Box
    spaces it takes the largest size along each axis, and each observation is padded
    with zeros at the end of every axis, so the real values stay at the front. For
    Discrete spaces it takes the range covering all of them and observations pass
    through unchanged. Every agent then reports that same space.

    Box spaces have to agree on dtype and number of dimensions. Anything other than Box
    and Discrete is rejected.

    An agent whose observation is already the full shape gets the array back without a
    copy, so writing into it writes into the environment.

    :param env: The AEC environment to wrap.
    """

    def __init__(self, env: AECEnv[AgentID, ObsType, ActionType]):
        assert isinstance(env, AECEnv), (
            "PadObservations is only compatible with AEC environments, "
            "use PadObservationsParallel instead."
        )
        assert hasattr(env, "possible_agents"), (
            "environment passed to PadObservations must have a possible_agents list."
        )
        super().__init__(env)
        spaces = [env.observation_space(agent) for agent in env.possible_agents]
        _check_paddable(spaces)
        self._obs_space = _padded_space(spaces)

    @override
    def observation_space(self, agent: AgentID) -> Space[Any]:
        return self._obs_space

    @override
    def observe(self, agent: AgentID) -> Any:
        return _pad_observation(self._obs_space, self.env.observe(agent))

    @override
    def __str__(self) -> str:
        return f"PadObservations<{self.env!s}>"


class PadObservationsParallel(BaseParallelWrapper[AgentID, Any, ActionType]):
    """Pads each agent's observation up to one shared observation space.

    The shared space covers the observation spaces of ``possible_agents``. For Box
    spaces it takes the largest size along each axis, and each observation is padded
    with zeros at the end of every axis, so the real values stay at the front. For
    Discrete spaces it takes the range covering all of them and observations pass
    through unchanged. Every agent then reports that same space.

    Box spaces have to agree on dtype and number of dimensions. Anything other than Box
    and Discrete is rejected.

    An agent whose observation is already the full shape gets the array back without a
    copy, so writing into it writes into the environment.

    :param env: The parallel environment to wrap.
    """

    def __init__(self, env: ParallelEnv[AgentID, ObsType, ActionType]):
        assert isinstance(env, ParallelEnv), (
            "PadObservationsParallel is only compatible with parallel environments, "
            "use PadObservations instead."
        )
        assert hasattr(env, "possible_agents"), (
            "environment passed to PadObservationsParallel must have a "
            "possible_agents list."
        )
        super().__init__(env)
        spaces = [env.observation_space(agent) for agent in env.possible_agents]
        _check_paddable(spaces)
        self._obs_space = _padded_space(spaces)

    @override
    def observation_space(self, agent: AgentID) -> Space[Any]:
        return self._obs_space

    def _pad(self, observations: dict[AgentID, Any]) -> dict[AgentID, Any]:
        return {
            agent: _pad_observation(self._obs_space, obs)
            for agent, obs in observations.items()
        }

    @override
    def reset(
        self, seed: int | None = None, options: dict[str, Any] | None = None
    ) -> tuple[dict[AgentID, Any], dict[AgentID, dict[str, Any]]]:
        observations, infos = self.env.reset(seed=seed, options=options)
        return self._pad(observations), infos

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
        return self._pad(observations), rewards, terminations, truncations, infos

    @override
    def __str__(self) -> str:
        return f"PadObservationsParallel<{self.env!s}>"
