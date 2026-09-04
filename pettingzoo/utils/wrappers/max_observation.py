"""Wrappers that reduce each agent's observation to a max over recent frames."""

from __future__ import annotations

import functools
from collections import deque
from typing import Any

import gymnasium.spaces
import numpy as np
from typing_extensions import override

from pettingzoo.utils.env import ActionType, AECEnv, AgentID, ObsType, ParallelEnv
from pettingzoo.utils.wrappers.base import BaseWrapper
from pettingzoo.utils.wrappers.base_parallel import BaseParallelWrapper

_ARRAY_SPACES = (
    gymnasium.spaces.Box,
    gymnasium.spaces.MultiBinary,
    gymnasium.spaces.MultiDiscrete,
)


def _check_memory(memory: int) -> int:
    if isinstance(memory, bool) or not isinstance(memory, (int, np.integer)):
        raise TypeError(f"memory must be an int, got {type(memory).__name__}")
    if memory < 1:
        raise ValueError(f"memory must be a positive int, got {memory}")
    return int(memory)


def _check_obs_space(
    name: str, agent: AgentID, space: gymnasium.spaces.Space[Any]
) -> None:
    if not isinstance(space, _ARRAY_SPACES):
        raise ValueError(
            f"{name} needs an array observation space, but agent {agent!r} has "
            f"{type(space).__name__}. Box, MultiBinary and MultiDiscrete are "
            "supported; Dict, Tuple and Discrete are not, because there is no "
            "elementwise max over them."
        )


def _check_possible_agents(wrapper: Any) -> None:
    """Fail at construction where we can. Envs that generate agents are checked later."""
    try:
        agents = wrapper.env.possible_agents
    except AttributeError:
        return
    for agent in agents:
        _check_obs_space(
            type(wrapper).__name__, agent, wrapper.env.observation_space(agent)
        )


def _reduce(history: deque[Any]) -> Any:
    # np.array copies, so a caller never gets a handle on the stored history and
    # cannot corrupt it. functools.reduce alone returns the stored frame itself
    # when the history holds only one.
    return np.array(functools.reduce(np.maximum, history))


class MaxObservationV1(BaseWrapper[AgentID, ObsType, ActionType]):
    """Replaces each agent's observation with the elementwise max over its last ``memory`` observations.

    This removes the flicker in environments that draw sprites on alternate frames.
    Histories are per agent and cleared on ``reset``, and the observation space is
    unchanged. Only array observation spaces work: Box, MultiBinary, MultiDiscrete.
    Ported from SuperSuit's max_observation_v0; the version suffix continues that numbering.

    :param env: The AEC environment to wrap.
    :param memory: How many observations to take the max over. Must be a positive int.
    """

    def __init__(self, env: AECEnv[AgentID, ObsType, ActionType], memory: int):
        assert isinstance(env, AECEnv), (
            "MaxObservationV1 is only compatible with AEC environments, "
            "use MaxObservationParallelV1 instead."
        )
        super().__init__(env)
        self.memory = _check_memory(memory)
        self._history: dict[AgentID, deque[Any]] = {}
        _check_possible_agents(self)

    def _record(self, agent: AgentID) -> None:
        """Add an agent's current observation to its history.

        Called from reset() and step(), for the agent whose turn it is, which is
        where SuperSuit records too. Recording inside observe() instead would make
        an agent's window depend on who reads it and how often, and would silently
        undo the max for anything that observes out of turn, such as a centralized
        critic or an observation logger.
        """
        obs = self.env.observe(agent)
        if obs is None:
            return
        _check_obs_space(type(self).__name__, agent, self.env.observation_space(agent))
        history = self._history.setdefault(agent, deque(maxlen=self.memory))
        history.append(np.array(obs))

    @override
    def reset(
        self, seed: int | None = None, options: dict[str, Any] | None = None
    ) -> None:
        self._history = {}
        super().reset(seed=seed, options=options)
        self._record(self.agent_selection)

    @override
    def step(self, action: ActionType) -> None:
        super().step(action)
        if self.agent_selection in self.agents:
            self._record(self.agent_selection)

    @override
    def observe(self, agent: AgentID) -> ObsType | None:
        # An agent that joined mid-episode has not had a turn yet.
        if agent not in self._history:
            return self.env.observe(agent)
        return _reduce(self._history[agent])

    @override
    def __str__(self) -> str:
        return f"MaxObservationV1<{self.env!s}>"


class MaxObservationParallelV1(BaseParallelWrapper[AgentID, ObsType, ActionType]):
    """Replaces each agent's observation with the elementwise max over its last ``memory`` observations.

    This removes the flicker in environments that draw sprites on alternate frames.
    Histories are per agent and cleared on ``reset``, and the observation space is
    unchanged. Only array observation spaces work: Box, MultiBinary, MultiDiscrete.
    Ported from SuperSuit's max_observation_v0; the version suffix continues that numbering.

    :param env: The parallel environment to wrap.
    :param memory: How many observations to take the max over. Must be a positive int.
    """

    def __init__(self, env: ParallelEnv[AgentID, ObsType, ActionType], memory: int):
        assert isinstance(env, ParallelEnv), (
            "MaxObservationParallelV1 is only compatible with parallel environments, "
            "use MaxObservationV1 instead."
        )
        super().__init__(env)
        self.memory = _check_memory(memory)
        self._history: dict[AgentID, deque[Any]] = {}
        _check_possible_agents(self)

    def _max_observations(
        self, observations: dict[AgentID, ObsType]
    ) -> dict[AgentID, ObsType]:
        maxed = {}
        for agent, obs in observations.items():
            _check_obs_space(
                type(self).__name__, agent, self.env.observation_space(agent)
            )
            history = self._history.setdefault(agent, deque(maxlen=self.memory))
            history.append(np.array(obs))
            maxed[agent] = _reduce(history)
        return maxed

    @override
    def reset(
        self, seed: int | None = None, options: dict[str, Any] | None = None
    ) -> tuple[dict[AgentID, ObsType], dict[AgentID, dict[str, Any]]]:
        self._history = {}
        observations, infos = self.env.reset(seed=seed, options=options)
        return self._max_observations(observations), infos

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
        observations, rewards, terminations, truncations, infos = self.env.step(actions)
        return (
            self._max_observations(observations),
            rewards,
            terminations,
            truncations,
            infos,
        )

    @override
    def __str__(self) -> str:
        return f"MaxObservationParallelV1<{self.env!s}>"
