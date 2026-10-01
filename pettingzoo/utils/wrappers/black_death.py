"""Wrapper that keeps departed agents in a Parallel environment until it ends."""

from __future__ import annotations

from typing import Any

import numpy as np
from gymnasium.spaces import Box
from typing_extensions import override

from pettingzoo.utils.env import ActionType, AgentID, ObsType, ParallelEnv
from pettingzoo.utils.wrappers.base_parallel import BaseParallelWrapper


class BlackDeathParallelV4(BaseParallelWrapper[AgentID, ObsType, ActionType]):
    """Keeps agents that leave the environment until the whole episode ends.

    The agents present after :meth:`reset` stay in ``agents`` for the rest of the
    episode, even after they leave the underlying environment. This is useful for
    learning code that needs a fixed number of agents, such as a vector
    environment with one slot per agent.

    On the step an agent leaves the underlying environment, its real observation,
    reward and info are returned. On every later step it receives an all-zeros
    observation with the shape and dtype of its observation space, a reward of
    ``0.0`` and an empty info dict, whatever the underlying environment returns
    for it, and any action sent for it is ignored. Only the actions of agents
    still in the underlying environment are forwarded.

    Termination and truncation flags:

    * Until the whole episode ends, a departed agent is reported with
      ``termination=False`` and ``truncation=False``, both on the step it leaves
      and on every later step, because it is still in ``agents``.
    * When the last agent leaves the underlying environment, every agent is
      reported done and ``agents`` becomes empty. Agents that were active on
      that step get the flags of the underlying environment. Departed agents get
      the flags they had on the step they left, so an agent that terminated
      early is still reported as terminated even if the episode was truncated.
      An agent that left without either flag set is reported as terminated.

    Only ``Box`` observation spaces whose bounds contain zero are supported.
    Agents that join the underlying environment after :meth:`reset` are not
    supported.

    This is the class-based replacement for SuperSuit's ``black_death_v3``, which
    reported the same value for both flags of every agent.

    :param env: The parallel environment to wrap.
    """

    def __init__(self, env: ParallelEnv[AgentID, ObsType, ActionType]):
        super().__init__(env)
        self.agents: list[AgentID] = []
        self._departed: dict[AgentID, tuple[bool, bool]] = {}

    def _black_obs(self, agent: AgentID) -> Any:
        space = self.observation_space(agent)
        assert isinstance(space, Box)
        return np.zeros(space.shape, dtype=space.dtype)

    def _check_space(self, agent: AgentID) -> None:
        space = self.observation_space(agent)
        if not isinstance(space, Box):
            raise ValueError(
                "BlackDeathParallelV4 only supports Box observation spaces, "
                f"agent {agent!r} has {space}."
            )
        if not (np.all(space.low <= 0) and np.all(space.high >= 0)):
            raise ValueError(
                "BlackDeathParallelV4 returns all-zeros observations for departed "
                f"agents, but zero is outside the observation space of agent "
                f"{agent!r}: {space}."
            )

    @override
    def reset(
        self, seed: int | None = None, options: dict[str, Any] | None = None
    ) -> tuple[dict[AgentID, ObsType], dict[AgentID, dict[str, Any]]]:
        observations, infos = self.env.reset(seed=seed, options=options)
        self.agents = self.env.agents[:]
        self._departed = {}
        for agent in self.agents:
            self._check_space(agent)
        return observations, infos

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
        active = self.env.agents[:]
        observations, rewards, terminations, truncations, infos = self.env.step(
            {agent: actions[agent] for agent in active}
        )

        still_active = set(self.env.agents)
        for agent in active:
            if agent not in still_active:
                terminated = bool(terminations.get(agent, False))
                truncated = bool(truncations.get(agent, False))
                self._departed[agent] = (terminated or not truncated, truncated)

        episode_over = not still_active
        out_obs = {}
        out_rewards = {}
        out_terminations = {}
        out_truncations = {}
        out_infos = {}
        for agent in self.agents:
            if agent in active:
                out_obs[agent] = (
                    observations[agent]
                    if agent in observations
                    else self._black_obs(agent)
                )
                out_rewards[agent] = rewards.get(agent, 0.0)
                out_infos[agent] = infos.get(agent, {})
            else:
                out_obs[agent] = self._black_obs(agent)
                out_rewards[agent] = 0.0
                out_infos[agent] = {}
            if episode_over:
                terminated, truncated = self._departed[agent]
            else:
                terminated, truncated = False, False
            out_terminations[agent] = terminated
            out_truncations[agent] = truncated

        if episode_over:
            self.agents = []
        return out_obs, out_rewards, out_terminations, out_truncations, out_infos

    @override
    def __str__(self) -> str:
        return f"BlackDeathParallelV4<{self.env!s}>"
