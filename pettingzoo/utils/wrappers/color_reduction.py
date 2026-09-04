from __future__ import annotations

from typing import Any

import gymnasium.spaces
import numpy as np
from typing_extensions import override

from pettingzoo.utils.env import ActionType, AECEnv, AgentID, ObsType, ParallelEnv
from pettingzoo.utils.wrappers.base import BaseWrapper
from pettingzoo.utils.wrappers.base_parallel import BaseParallelWrapper

COLOR_REDUCTION_MODES = ("full", "R", "G", "B")
GRAYSCALE_WEIGHTS = np.array([0.299, 0.587, 0.114], dtype=np.float32)
_CHANNELS = {"R": 0, "G": 1, "B": 2}


def _check_mode(mode: str) -> None:
    assert mode in COLOR_REDUCTION_MODES, (
        f"mode must be one of {list(COLOR_REDUCTION_MODES)}, got {mode!r}"
    )


def _reduce(obs: np.ndarray, mode: str) -> np.ndarray:
    if mode == "full":
        return (np.asarray(obs, dtype=np.float32) @ GRAYSCALE_WEIGHTS).astype(np.uint8)
    return np.asarray(obs)[:, :, _CHANNELS[mode]].copy()


def _reduced_space(
    space: gymnasium.spaces.Space[Any], mode: str, agent: Any
) -> gymnasium.spaces.Box:
    assert (
        isinstance(space, gymnasium.spaces.Box)
        and len(space.shape) == 3
        and space.shape[2] == 3
    ), (
        "color reduction needs a 3d Box observation space with a last dimension of "
        f"size 3, got {space} for agent {agent}"
    )
    low = _reduce(space.low, mode)
    high = _reduce(space.high, mode)
    return gymnasium.spaces.Box(low=low, high=high, dtype=low.dtype.type)


class ColorReductionObservationV1(BaseWrapper[AgentID, Any, ActionType]):
    """Reduces an image observation to a single channel.

    ``"full"`` converts to grayscale with the luminance weights
    [0.299, 0.587, 0.114] and returns uint8 whatever the input dtype was. ``"R"``,
    ``"G"`` and ``"B"`` take the named channel and keep the input dtype. Either way
    the trailing channel axis is dropped, so an (H, W, 3) observation becomes (H, W).

    :param env: The AEC environment to wrap.
    :param mode: One of "full", "R", "G", "B".
    """

    def __init__(self, env: AECEnv[AgentID, ObsType, ActionType], mode: str = "full"):
        assert isinstance(env, AECEnv), (
            "ColorReductionObservationV1 is only compatible with AEC environments, "
            "use ColorReductionObservationParallelV1 instead."
        )
        _check_mode(mode)
        super().__init__(env)
        self.mode = mode
        self._obs_spaces: dict[AgentID, gymnasium.spaces.Box] = {}
        # SuperSuit checks the spaces when you wrap rather than on first use, and
        # skips the check for envs that have no possible_agents to check yet.
        for known_agent in getattr(env, "possible_agents", []):
            self.observation_space(known_agent)

    @override
    def observation_space(self, agent: AgentID) -> gymnasium.spaces.Box:
        if agent not in self._obs_spaces:
            self._obs_spaces[agent] = _reduced_space(
                self.env.observation_space(agent), self.mode, agent
            )
        return self._obs_spaces[agent]

    @override
    def observe(self, agent: AgentID) -> Any:
        obs = self.env.observe(agent)
        if obs is None:
            return None
        return _reduce(obs, self.mode)

    @override
    def __str__(self) -> str:
        return f"ColorReductionObservationV1<{self.env!s}>"


class ColorReductionObservationParallelV1(BaseParallelWrapper[AgentID, Any, ActionType]):
    """Reduces an image observation to a single channel.

    ``"full"`` converts to grayscale with the luminance weights
    [0.299, 0.587, 0.114] and returns uint8 whatever the input dtype was. ``"R"``,
    ``"G"`` and ``"B"`` take the named channel and keep the input dtype. Either way
    the trailing channel axis is dropped, so an (H, W, 3) observation becomes (H, W).

    :param env: The parallel environment to wrap.
    :param mode: One of "full", "R", "G", "B".
    """

    def __init__(
        self, env: ParallelEnv[AgentID, ObsType, ActionType], mode: str = "full"
    ):
        _check_mode(mode)
        super().__init__(env)
        self.mode = mode
        self._obs_spaces: dict[AgentID, gymnasium.spaces.Box] = {}
        # SuperSuit checks the spaces when you wrap rather than on first use, and
        # skips the check for envs that have no possible_agents to check yet.
        for known_agent in getattr(env, "possible_agents", []):
            self.observation_space(known_agent)

    @override
    def observation_space(self, agent: AgentID) -> gymnasium.spaces.Box:
        if agent not in self._obs_spaces:
            self._obs_spaces[agent] = _reduced_space(
                self.env.observation_space(agent), self.mode, agent
            )
        return self._obs_spaces[agent]

    def _reduce_all(self, observations: dict[AgentID, Any]) -> dict[AgentID, Any]:
        return {agent: _reduce(obs, self.mode) for agent, obs in observations.items()}

    @override
    def reset(
        self, seed: int | None = None, options: dict[str, Any] | None = None
    ) -> tuple[dict[AgentID, Any], dict[AgentID, dict[str, Any]]]:
        observations, infos = self.env.reset(seed=seed, options=options)
        return self._reduce_all(observations), infos

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
        return self._reduce_all(observations), rewards, terminations, truncations, infos

    @override
    def __str__(self) -> str:
        return f"ColorReductionObservationParallelV1<{self.env!s}>"
