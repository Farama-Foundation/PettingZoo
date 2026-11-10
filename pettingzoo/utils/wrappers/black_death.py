"""Wrapper that keeps departed Parallel agents visible until episode end."""

from __future__ import annotations

from typing import Any

import gymnasium.spaces
import numpy as np
from gymnasium.spaces import Box
from typing_extensions import override

from pettingzoo.utils.env import ActionType, AgentID, ParallelEnv
from pettingzoo.utils.wrappers.base_parallel import BaseParallelWrapper


def _box_observation_space(space: gymnasium.spaces.Space[Any], agent: AgentID) -> Box:
    """Return a Box observation space or raise a clear compatibility error."""
    if not isinstance(space, Box):
        raise TypeError(
            "BlackDeathParallelV4 only supports Box observation spaces, "
            f"but agent {agent!r} has {space}."
        )
    return space


class BlackDeathParallelV4(BaseParallelWrapper[AgentID, Any, ActionType]):
    """Keep the reset-time agent set visible until the whole episode ends.

    When an agent leaves the wrapped environment early, subsequent steps expose
    a zero-valued observation with the same shape and dtype as that agent's Box
    observation space, zero reward, and an empty info dictionary. Actions for
    departed agents are ignored and only actions for currently active wrapped
    agents are forwarded.

    To keep the public agent set stable, an early departure is reported as
    terminated=False and truncated=False until the underlying episode ends.
    The wrapper remembers the original cause of each departure and reports those
    per-agent termination and truncation flags on the final step instead of
    collapsing both causes into one done flag.

    Agents that appear after reset are not supported because they would change
    the fixed agent set exposed by this wrapper.

    :param env: The Parallel environment to wrap.
    """

    def __init__(self, env: ParallelEnv[AgentID, Any, ActionType]):
        super().__init__(env)
        self._episode_agents: list[AgentID] = []
        self._zero_observations: dict[AgentID, np.ndarray] = {}
        self._stored_terminations: dict[AgentID, bool] = {}
        self._stored_truncations: dict[AgentID, bool] = {}

        for agent in getattr(env, "possible_agents", []):
            _box_observation_space(self.env.observation_space(agent), agent)

    @override
    def reset(
        self, seed: int | None = None, options: dict[str, Any] | None = None
    ) -> tuple[dict[AgentID, Any], dict[AgentID, dict[str, Any]]]:
        observations, infos = self.env.reset(seed=seed, options=options)

        self._episode_agents = list(self.env.agents)
        self.agents = self._episode_agents.copy()
        self._stored_terminations = dict.fromkeys(self._episode_agents, False)
        self._stored_truncations = dict.fromkeys(self._episode_agents, False)
        self._zero_observations = {}

        for agent in self._episode_agents:
            space = _box_observation_space(self.env.observation_space(agent), agent)
            self._zero_observations[agent] = np.zeros(space.shape, dtype=space.dtype)

        return (
            {
                agent: observations.get(agent, self._zero_observations[agent].copy())
                for agent in self._episode_agents
            },
            {agent: infos.get(agent, {}) for agent in self._episode_agents},
        )

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
        active_agents = list(self.env.agents)
        unexpected = [
            agent for agent in active_agents if agent not in self._episode_agents
        ]
        if unexpected:
            raise RuntimeError(
                "BlackDeathParallelV4 does not support agents appearing after reset: "
                f"{unexpected}."
            )

        active_actions = {agent: actions[agent] for agent in active_agents}
        observations, rewards, terminations, truncations, infos = self.env.step(
            active_actions
        )

        unexpected = [
            agent for agent in self.env.agents if agent not in self._episode_agents
        ]
        if unexpected:
            raise RuntimeError(
                "BlackDeathParallelV4 does not support agents appearing after reset: "
                f"{unexpected}."
            )

        for agent in self._episode_agents:
            if terminations.get(agent, False):
                self._stored_terminations[agent] = True
            if truncations.get(agent, False):
                self._stored_truncations[agent] = True

        episode_done = not self.env.agents
        if episode_done:
            total_terminations = self._stored_terminations.copy()
            total_truncations = self._stored_truncations.copy()
            self.agents = []
        else:
            total_terminations = dict.fromkeys(self._episode_agents, False)
            total_truncations = dict.fromkeys(self._episode_agents, False)
            self.agents = self._episode_agents.copy()

        total_observations = {
            agent: observations.get(agent, self._zero_observations[agent].copy())
            for agent in self._episode_agents
        }
        total_rewards = {
            agent: rewards.get(agent, 0.0) for agent in self._episode_agents
        }
        total_infos = {agent: infos.get(agent, {}) for agent in self._episode_agents}

        return (
            total_observations,
            total_rewards,
            total_terminations,
            total_truncations,
            total_infos,
        )

    @override
    def __str__(self) -> str:
        return f"BlackDeathParallelV4<{self.env!s}>"
