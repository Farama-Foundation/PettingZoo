from __future__ import annotations

from typing import Any

import numpy as np
from gymnasium.spaces import Box, Space
from typing_extensions import override

from pettingzoo.utils.env import ActionType, AECEnv, AgentID, ObsType, ParallelEnv
from pettingzoo.utils.wrappers.base import BaseWrapper
from pettingzoo.utils.wrappers.base_parallel import BaseParallelWrapper


def _check_range(min_obs: float, max_obs: float) -> None:
    assert max_obs > min_obs, (
        f"max_obs must be greater than min_obs, got min_obs={min_obs} and max_obs={max_obs}."
    )


def _rescaled_space(
    space: Space[Any], min_obs: float, max_obs: float
) -> tuple[Box, Box]:
    """Check that space can be rescaled and return it next to its rescaled version."""
    assert isinstance(space, Box), (
        f"RescaleObservationV1 only works with Box observation spaces, got {space}."
    )
    space_dtype = np.dtype(space.dtype)
    assert space_dtype in (np.dtype(np.float32), np.dtype(np.float64)), (
        "RescaleObservationV1 only works with float32 or float64 Box observation "
        f"spaces, got dtype {space.dtype}."
    )
    assert np.all(np.isfinite(space.low)) and np.all(np.isfinite(space.high)), (
        "RescaleObservationV1 needs finite bounds to rescale from, but the observation "
        f"space {space} has infinite bounds."
    )
    assert np.all(space.high > space.low), (
        "RescaleObservationV1 needs every element of the observation space to have "
        f"high > low, but the space {space} has an element with no width."
    )
    dtype = np.float64 if space_dtype == np.dtype(np.float64) else np.float32
    return space, Box(low=min_obs, high=max_obs, shape=space.shape, dtype=dtype)


def _rescale(
    obs: Any, space: Box, rescaled: Box, min_obs: float, max_obs: float
) -> np.ndarray[Any, Any]:
    """Map obs from the bounds of space onto [min_obs, max_obs], element by element.

    The arithmetic runs in float64 whatever the space dtype is. In float32 the
    intermediate width can overflow to infinity, and rounding disagrees with the
    cast gymnasium applies to the target bounds, which puts endpoints just outside
    the rescaled space. The clip covers what is left of that.
    """
    low = space.low.astype(np.float64)
    high = space.high.astype(np.float64)
    scaled = (np.asarray(obs, dtype=np.float64) - low) / (high - low)
    result = (scaled * (max_obs - min_obs) + min_obs).astype(space.dtype)
    return np.clip(result, rescaled.low, rescaled.high)


class RescaleObservationV1(BaseWrapper[AgentID, Any, ActionType]):
    """Linearly rescales each agent's Box observation into a fixed range.

    Every element is mapped from its own ``[low, high]`` in the wrapped space onto
    ``[min_obs, max_obs]``, and the result is clipped so it always sits inside the
    advertised space. The wrapped space has to be a float Box whose elements all
    have finite ``low`` and ``high`` with ``high > low``, since anything else
    gives nothing to scale from. Every space in ``possible_agents`` is checked
    when the wrapper is built.

    Ported from SuperSuit's normalize_obs_v0; the version suffix continues that numbering.

    :param env: The AEC environment to wrap.
    :param min_obs: Lower bound of the rescaled observations.
    :param max_obs: Upper bound of the rescaled observations.
    """

    def __init__(
        self,
        env: AECEnv[AgentID, ObsType, ActionType],
        min_obs: float = 0.0,
        max_obs: float = 1.0,
    ):
        assert isinstance(env, AECEnv), (
            "RescaleObservationV1 is only compatible with AEC environments, "
            "use RescaleObservationParallelV1 instead."
        )
        _check_range(min_obs, max_obs)
        super().__init__(env)
        self.min_obs = min_obs
        self.max_obs = max_obs
        self._spaces: dict[AgentID, tuple[Box, Box]] = {}
        for agent in self.env.possible_agents:
            self._spaces_for(agent)

    def _spaces_for(self, agent: AgentID) -> tuple[Box, Box]:
        if agent not in self._spaces:
            self._spaces[agent] = _rescaled_space(
                self.env.observation_space(agent), self.min_obs, self.max_obs
            )
        return self._spaces[agent]

    @override
    def observation_space(self, agent: AgentID) -> Box:
        return self._spaces_for(agent)[1]

    @override
    def observe(self, agent: AgentID) -> Any:
        obs = self.env.observe(agent)
        if obs is None:
            return None
        space, rescaled = self._spaces_for(agent)
        return _rescale(obs, space, rescaled, self.min_obs, self.max_obs)

    @override
    def __str__(self) -> str:
        return f"RescaleObservationV1<{self.env!s}>"


class RescaleObservationParallelV1(BaseParallelWrapper[AgentID, Any, ActionType]):
    """Linearly rescales each agent's Box observation into a fixed range.

    Every element is mapped from its own ``[low, high]`` in the wrapped space onto
    ``[min_obs, max_obs]``, and the result is clipped so it always sits inside the
    advertised space. The wrapped space has to be a float Box whose elements all
    have finite ``low`` and ``high`` with ``high > low``, since anything else
    gives nothing to scale from. Every space in ``possible_agents`` is checked
    when the wrapper is built.

    Ported from SuperSuit's normalize_obs_v0; the version suffix continues that numbering.

    :param env: The parallel environment to wrap.
    :param min_obs: Lower bound of the rescaled observations.
    :param max_obs: Upper bound of the rescaled observations.
    """

    def __init__(
        self,
        env: ParallelEnv[AgentID, ObsType, ActionType],
        min_obs: float = 0.0,
        max_obs: float = 1.0,
    ):
        _check_range(min_obs, max_obs)
        super().__init__(env)
        self.min_obs = min_obs
        self.max_obs = max_obs
        self._spaces: dict[AgentID, tuple[Box, Box]] = {}
        for agent in self.env.possible_agents:
            self._spaces_for(agent)

    def _spaces_for(self, agent: AgentID) -> tuple[Box, Box]:
        if agent not in self._spaces:
            self._spaces[agent] = _rescaled_space(
                self.env.observation_space(agent), self.min_obs, self.max_obs
            )
        return self._spaces[agent]

    @override
    def observation_space(self, agent: AgentID) -> Box:
        return self._spaces_for(agent)[1]

    def _rescale_all(self, observations: dict[AgentID, Any]) -> dict[AgentID, Any]:
        return {
            agent: _rescale(obs, *self._spaces_for(agent), self.min_obs, self.max_obs)
            for agent, obs in observations.items()
        }

    @override
    def reset(
        self, seed: int | None = None, options: dict[str, Any] | None = None
    ) -> tuple[dict[AgentID, Any], dict[AgentID, dict[str, Any]]]:
        observations, infos = self.env.reset(seed=seed, options=options)
        return self._rescale_all(observations), infos

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
            self._rescale_all(observations),
            rewards,
            terminations,
            truncations,
            infos,
        )

    @override
    def __str__(self) -> str:
        return f"RescaleObservationParallelV1<{self.env!s}>"
