from __future__ import annotations

from typing import Any, cast

import gymnasium.spaces
import numpy as np
from gymnasium.spaces import Box
from typing_extensions import override

from pettingzoo.utils.env import ActionType, AECEnv, AgentID, ObsType, ParallelEnv
from pettingzoo.utils.wrappers.base import BaseWrapper
from pettingzoo.utils.wrappers.base_parallel import BaseParallelWrapper


def _check_shape(shape: tuple[int, ...]) -> None:
    assert isinstance(shape, tuple), f"shape must be a tuple, is {shape}"
    assert len(shape) > 0, "shape must not be empty"
    assert all(np.issubdtype(type(element), np.integer) for element in shape), (
        f"shape must be a tuple of ints, is {shape}"
    )
    assert all(element != -1 for element in shape), (
        f"-1 is not supported, give the size of every axis. shape is {shape}"
    )
    assert all(element > 0 for element in shape), (
        f"shape must be a tuple of positive ints, is {shape}"
    )


def _reshaped_space(
    space: gymnasium.spaces.Space[Any], shape: tuple[int, ...], agent: AgentID
) -> Box:
    """Returns `space` reshaped to `shape`, keeping the per-element bounds."""
    assert isinstance(space, Box), (
        f"reshape is only defined for Box observation spaces, "
        f"the space of agent {agent} is {space}."
    )
    assert np.prod(shape) == np.prod(space.shape), (
        f"new shape {shape} must have as many elements as the observation "
        f"space of agent {agent}, which has shape {space.shape}."
    )
    # Box accepts a numpy dtype, its annotation just says otherwise.
    dtype = cast("type[np.floating[Any] | np.integer[Any]]", space.dtype)
    return Box(
        low=space.low.reshape(shape), high=space.high.reshape(shape), dtype=dtype
    )


class ReshapeObservation(BaseWrapper[AgentID, Any, ActionType]):
    """Reshapes each agent's observation to the given shape.

    The observation space is reshaped the same way, so per-element bounds are kept.
    Only works on Box observation spaces.

    :param env: The AEC environment to wrap.
    :param shape: The new observation shape. Must have as many elements as the old one.
    """

    def __init__(
        self, env: AECEnv[AgentID, ObsType, ActionType], shape: tuple[int, ...]
    ):
        assert isinstance(env, AECEnv), (
            "ReshapeObservation is only compatible with AEC environments, "
            "use ReshapeObservationParallel instead."
        )
        _check_shape(shape)
        super().__init__(env)
        self.shape = shape
        self._obs_spaces: dict[AgentID, Box] = {}
        # Fail on construction for envs that already know their agents. Envs that
        # only fill possible_agents in reset() are caught on the first observation.
        for agent in getattr(env, "possible_agents", []):
            self.observation_space(agent)

    @override
    def observation_space(self, agent: AgentID) -> Box:
        if agent not in self._obs_spaces:
            self._obs_spaces[agent] = _reshaped_space(
                self.env.observation_space(agent), self.shape, agent
            )
        return self._obs_spaces[agent]

    @override
    def observe(self, agent: AgentID) -> np.ndarray | None:
        # Checks the shape against this agent's space. Cached after the first call.
        self.observation_space(agent)
        obs = self.env.observe(agent)
        if obs is None:
            return None
        return np.reshape(obs, self.shape)

    @override
    def __str__(self) -> str:
        return f"ReshapeObservation<{self.env!s}>"


class ReshapeObservationParallel(BaseParallelWrapper[AgentID, Any, ActionType]):
    """Reshapes each agent's observation to the given shape.

    The observation space is reshaped the same way, so per-element bounds are kept.
    Only works on Box observation spaces.

    :param env: The parallel environment to wrap.
    :param shape: The new observation shape. Must have as many elements as the old one.
    """

    def __init__(
        self, env: ParallelEnv[AgentID, ObsType, ActionType], shape: tuple[int, ...]
    ):
        _check_shape(shape)
        super().__init__(env)
        self.shape = shape
        self._obs_spaces: dict[AgentID, Box] = {}
        # Fail on construction for envs that already know their agents. Envs that
        # only fill possible_agents in reset() are caught on the first observation.
        for agent in getattr(env, "possible_agents", []):
            self.observation_space(agent)

    @override
    def observation_space(self, agent: AgentID) -> Box:
        if agent not in self._obs_spaces:
            self._obs_spaces[agent] = _reshaped_space(
                self.env.observation_space(agent), self.shape, agent
            )
        return self._obs_spaces[agent]

    def _reshape(self, observations: dict[AgentID, Any]) -> dict[AgentID, np.ndarray]:
        reshaped = {}
        for agent, obs in observations.items():
            # Checks the shape against this agent's space. Cached after the first call.
            self.observation_space(agent)
            reshaped[agent] = np.reshape(obs, self.shape)
        return reshaped

    @override
    def reset(
        self, seed: int | None = None, options: dict[str, Any] | None = None
    ) -> tuple[dict[AgentID, np.ndarray], dict[AgentID, dict[str, Any]]]:
        observations, infos = self.env.reset(seed=seed, options=options)
        return self._reshape(observations), infos

    @override
    def step(
        self, actions: dict[AgentID, ActionType]
    ) -> tuple[
        dict[AgentID, np.ndarray],
        dict[AgentID, float],
        dict[AgentID, bool],
        dict[AgentID, bool],
        dict[AgentID, dict[str, Any]],
    ]:
        observations, rewards, terminations, truncations, infos = self.env.step(actions)
        return self._reshape(observations), rewards, terminations, truncations, infos

    @override
    def __str__(self) -> str:
        return f"ReshapeObservationParallel<{self.env!s}>"
