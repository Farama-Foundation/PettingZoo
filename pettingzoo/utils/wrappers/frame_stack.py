"""Wrappers that stack each agent's recent observations into one observation."""

from __future__ import annotations

from collections import deque
from typing import Any, Generic, cast

import gymnasium.spaces
import numpy as np
from gymnasium.spaces import Box, Discrete
from typing_extensions import override

from pettingzoo.utils.env import ActionType, AECEnv, AgentID, ObsType, ParallelEnv
from pettingzoo.utils.wrappers.base import BaseWrapper
from pettingzoo.utils.wrappers.base_parallel import BaseParallelWrapper

_INITIAL_MODES = ("zeros", "first_obs")
_INT64_MAX = int(np.iinfo(np.int64).max)


def _check_stack_size(stack_size: int) -> int:
    if isinstance(stack_size, bool) or not isinstance(stack_size, (int, np.integer)):
        raise TypeError(f"stack_size must be an int, got {type(stack_size).__name__}")
    if stack_size < 1:
        raise ValueError(f"stack_size must be a positive int, got {stack_size}")
    return int(stack_size)


def _check_stack_dim(stack_dim: int) -> int:
    if (
        isinstance(stack_dim, bool)
        or not isinstance(stack_dim, (int, np.integer))
        or stack_dim not in (0, -1)
    ):
        raise ValueError(f"stack_dim must be 0 or -1, got {stack_dim!r}")
    return int(stack_dim)


def _check_initial(initial: str) -> str:
    if initial not in _INITIAL_MODES:
        raise ValueError(f"initial must be one of {_INITIAL_MODES}, got {initial!r}")
    return initial


def _stack_frames(frames: list[np.ndarray], stack_dim: int) -> np.ndarray:
    """Stacks frames, oldest first, the same way SuperSuit's frame_stack does.

    1D frames are concatenated. 2D frames get a new stacking axis, last or first.
    3D frames are concatenated along the channel axis, last or first.
    """
    if frames[0].ndim == 2:
        return np.stack(frames, axis=stack_dim)
    return np.concatenate(frames, axis=0 if frames[0].ndim == 1 else stack_dim)


class _FrameStacker(Generic[AgentID]):
    """The per-agent spaces and stacking logic shared by the AEC and parallel wrappers."""

    def __init__(
        self,
        name: str,
        base_space: Any,
        stack_size: int,
        stack_dim: int,
        initial: str,
    ):
        self.name = name
        self.base_space = base_space
        self.stack_size = _check_stack_size(stack_size)
        self.stack_dim = _check_stack_dim(stack_dim)
        self.initial = _check_initial(initial)
        self._spaces: dict[AgentID, tuple[Any, gymnasium.spaces.Space[Any]]] = {}

    def observation_space(self, agent: AgentID) -> gymnasium.spaces.Space[Any]:
        # Cached so the same space object comes back every time, which space
        # seeding relies on. Rebuilt if the env replaces the agent's space, as
        # envs that generate their agents may do on reset.
        base = self.base_space(agent)
        cached = self._spaces.get(agent)
        if cached is None or cached[0] is not base:
            cached = (base, self._stacked_space(agent, base))
            self._spaces[agent] = cached
        return cached[1]

    def _stacked_space(
        self, agent: AgentID, space: gymnasium.spaces.Space[Any]
    ) -> gymnasium.spaces.Space[Any]:
        if isinstance(space, Box):
            if not 1 <= len(space.shape) <= 3:
                raise ValueError(
                    f"{self.name} only stacks 1, 2 or 3 dimensional Box "
                    f"observations, but agent {agent!r} has shape {space.shape}."
                )
            low = _stack_frames([space.low] * self.stack_size, self.stack_dim)
            high = _stack_frames([space.high] * self.stack_size, self.stack_dim)
            if self.initial == "zeros":
                # Zero-filled frames have to be inside the advertised space too.
                low = np.minimum(low, 0)
                high = np.maximum(high, 0)
            # Box accepts a numpy dtype, its annotation just says otherwise.
            dtype = cast("type[np.floating[Any] | np.integer[Any]]", space.dtype)
            return Box(low=low, high=high, dtype=dtype)
        if isinstance(space, Discrete):
            n = int(space.n) ** self.stack_size
            if n > _INT64_MAX:
                raise ValueError(
                    f"{self.name} would need a Discrete({space.n}**{self.stack_size}) "
                    f"observation space for agent {agent!r}, which does not fit "
                    "in an int64. Use a smaller stack_size."
                )
            return Discrete(n)
        raise ValueError(
            f"{self.name} only stacks Box and Discrete observations, but agent "
            f"{agent!r} has {type(space).__name__}."
        )

    def frame(self, agent: AgentID, obs: Any) -> Any:
        """Copies an observation into the form the history stores."""
        # Also checks the agent's space, for envs whose agents are only known after reset.
        self.observation_space(agent)
        space = self.base_space(agent)
        if isinstance(space, Discrete):
            # A digit in base n, so a Discrete space with a nonzero start encodes correctly.
            return int(obs) - int(space.start)
        return np.array(obs, dtype=space.dtype)

    def new_history(self, agent: AgentID, frame: Any) -> deque[Any]:
        """Starts a full history whose newest frame is ``frame``."""
        history: deque[Any] = deque(maxlen=self.stack_size)
        if self.initial == "zeros":
            history.extend([np.zeros_like(frame)] * (self.stack_size - 1))
        else:
            history.extend([frame] * (self.stack_size - 1))
        history.append(frame)
        return history

    def build(self, agent: AgentID, history: deque[Any]) -> Any:
        """Turns a history into a stacked observation. Always returns a fresh object."""
        space = self.base_space(agent)
        if isinstance(space, Discrete):
            # The newest frame is the least significant digit, as in SuperSuit.
            code = 0
            for digit in history:
                code = code * int(space.n) + int(digit)
            return np.int64(code)
        return _stack_frames(list(history), self.stack_dim)


def _check_possible_agents(stacker: _FrameStacker[Any], env: Any) -> None:
    """Fail at construction where we can. Envs that generate agents are checked later."""
    for agent in getattr(env, "possible_agents", []):
        stacker.observation_space(agent)


class FrameStackV3(BaseWrapper[AgentID, Any, ActionType]):
    """Stacks each agent's last ``stack_size`` observations into one observation.

    Box observations with 1, 2 or 3 dimensions are stacked as in SuperSuit: 1D
    frames are concatenated, 2D frames get a new last (``stack_dim=-1``) or first
    (``stack_dim=0``) axis, and 3D frames are concatenated along the last or first
    (channel) axis. A ``Discrete(n)`` observation becomes one ``Discrete(n**stack_size)``
    observation with the newest frame as the least significant base-``n`` digit
    (each digit is the observation minus the space's ``start``).
    The observation space is updated to match and keeps the dtype.

    ``initial`` says what fills the history before an agent has ``stack_size`` frames:
    ``"first_obs"`` repeats the agent's first observation (SuperSuit's frame_stack_v2)
    and ``"zeros"`` fills it with zeros (SuperSuit's frame_stack_v1). In ``"zeros"`` mode
    the Box bounds are widened to include 0. The version suffix continues SuperSuit's
    numbering.

    An agent's history advances at the start of each of its turns, after ``reset`` or
    ``step``, so ``observe`` never changes it: reading an observation any number of
    times, or reading another agent's, returns the same stack until the next turn.
    Histories are per agent and cleared on ``reset``. An agent that has not had a
    turn yet sees the stack its current observation would start. An agent's history
    is dropped when it leaves ``agents``, so an agent that comes back starts fresh.

    :param env: The AEC environment to wrap.
    :param stack_size: How many observations to stack. Must be a positive int.
    :param stack_dim: The axis to stack along, ``-1`` (last) or ``0`` (first).
    :param initial: ``"first_obs"`` or ``"zeros"``, what fills the history at first.
    """

    def __init__(
        self,
        env: AECEnv[AgentID, ObsType, ActionType],
        stack_size: int = 4,
        stack_dim: int = -1,
        initial: str = "first_obs",
    ):
        assert isinstance(env, AECEnv), (
            "FrameStackV3 is only compatible with AEC environments, "
            "use FrameStackParallelV3 instead."
        )
        super().__init__(env)
        self._stacker = _FrameStacker(
            type(self).__name__,
            self.env.observation_space,
            stack_size,
            stack_dim,
            initial,
        )
        self.stack_size = self._stacker.stack_size
        self.stack_dim = self._stacker.stack_dim
        self.initial = self._stacker.initial
        self._history: dict[AgentID, deque[Any]] = {}
        _check_possible_agents(self._stacker, env)

    @override
    def observation_space(self, agent: AgentID) -> gymnasium.spaces.Space[Any]:
        return self._stacker.observation_space(agent)

    def _record(self, agent: AgentID) -> None:
        """Add an agent's current observation to its history.

        Called from reset() and step(), for the agent whose turn it is, which is
        where SuperSuit records too. Recording inside observe() instead would make
        an agent's stack depend on who reads it and how often.
        """
        obs = self.env.observe(agent)
        if obs is None:
            return
        frame = self._stacker.frame(agent, obs)
        if agent in self._history:
            self._history[agent].append(frame)
        else:
            self._history[agent] = self._stacker.new_history(agent, frame)

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
        self._history = {
            agent: history
            for agent, history in self._history.items()
            if agent in self.env.agents
        }
        if self.agent_selection in self.env.agents:
            self._record(self.agent_selection)

    @override
    def observe(self, agent: AgentID) -> Any:
        history = self._history.get(agent)
        if history is None:
            # No turn yet. Show what the first turn would start with, but do not
            # store it: the history only advances on turns.
            obs = self.env.observe(agent)
            if obs is None:
                return None
            history = self._stacker.new_history(agent, self._stacker.frame(agent, obs))
        return self._stacker.build(agent, history)

    @override
    def __str__(self) -> str:
        return f"FrameStackV3<{self.env!s}>"


class FrameStackParallelV3(BaseParallelWrapper[AgentID, Any, ActionType]):
    """Stacks each agent's last ``stack_size`` observations into one observation.

    Box observations with 1, 2 or 3 dimensions are stacked as in SuperSuit: 1D
    frames are concatenated, 2D frames get a new last (``stack_dim=-1``) or first
    (``stack_dim=0``) axis, and 3D frames are concatenated along the last or first
    (channel) axis. A ``Discrete(n)`` observation becomes one ``Discrete(n**stack_size)``
    observation with the newest frame as the least significant base-``n`` digit
    (each digit is the observation minus the space's ``start``).
    The observation space is updated to match and keeps the dtype.

    ``initial`` says what fills the history before an agent has ``stack_size`` frames:
    ``"first_obs"`` repeats the agent's first observation (SuperSuit's frame_stack_v2)
    and ``"zeros"`` fills it with zeros (SuperSuit's frame_stack_v1). In ``"zeros"`` mode
    the Box bounds are widened to include 0. The version suffix continues SuperSuit's
    numbering.

    An agent's history advances each time ``reset`` or ``step`` returns an observation
    for it. Histories are per agent and cleared on ``reset``. An agent's history starts
    with the first observation returned for it, and is dropped once a step returns no
    observation for it, so an agent that comes back starts fresh.

    :param env: The parallel environment to wrap.
    :param stack_size: How many observations to stack. Must be a positive int.
    :param stack_dim: The axis to stack along, ``-1`` (last) or ``0`` (first).
    :param initial: ``"first_obs"`` or ``"zeros"``, what fills the history at first.
    """

    def __init__(
        self,
        env: ParallelEnv[AgentID, ObsType, ActionType],
        stack_size: int = 4,
        stack_dim: int = -1,
        initial: str = "first_obs",
    ):
        assert isinstance(env, ParallelEnv), (
            "FrameStackParallelV3 is only compatible with parallel environments, "
            "use FrameStackV3 instead."
        )
        super().__init__(env)
        self._stacker = _FrameStacker(
            type(self).__name__,
            self.env.observation_space,
            stack_size,
            stack_dim,
            initial,
        )
        self.stack_size = self._stacker.stack_size
        self.stack_dim = self._stacker.stack_dim
        self.initial = self._stacker.initial
        self._history: dict[AgentID, deque[Any]] = {}
        _check_possible_agents(self._stacker, env)

    @override
    def observation_space(self, agent: AgentID) -> gymnasium.spaces.Space[Any]:
        return self._stacker.observation_space(agent)

    def _stack_observations(
        self, observations: dict[AgentID, Any]
    ) -> dict[AgentID, Any]:
        stacked = {}
        for agent, obs in observations.items():
            frame = self._stacker.frame(agent, obs)
            if agent in self._history:
                self._history[agent].append(frame)
            else:
                self._history[agent] = self._stacker.new_history(agent, frame)
            stacked[agent] = self._stacker.build(agent, self._history[agent])
        self._history = {
            agent: history
            for agent, history in self._history.items()
            if agent in observations
        }
        return stacked

    @override
    def reset(
        self, seed: int | None = None, options: dict[str, Any] | None = None
    ) -> tuple[dict[AgentID, Any], dict[AgentID, dict[str, Any]]]:
        self._history = {}
        observations, infos = self.env.reset(seed=seed, options=options)
        return self._stack_observations(observations), infos

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
            self._stack_observations(observations),
            rewards,
            terminations,
            truncations,
            infos,
        )

    @override
    def __str__(self) -> str:
        return f"FrameStackParallelV3<{self.env!s}>"
