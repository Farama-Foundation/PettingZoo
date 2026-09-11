from __future__ import annotations

import copy
from typing import Any

from typing_extensions import override

from pettingzoo.utils.env import ActionType, AgentID, ObsType, ParallelEnv
from pettingzoo.utils.wrappers.base_parallel import BaseParallelWrapper


class MultiEpisodeParallelEnv(BaseParallelWrapper[AgentID, ObsType, ActionType]):
    """Creates a new environment using the base environment that runs for `num_episodes` before truncating.

    This is useful for creating evaluation environments.
    When there are no more valid agents in the underlying environment, the environment is automatically reset.
    When this happens, the `observation` and `info` returned by `step()` are replaced with that of the reset environment.
    The result of this wrapper is that the environment is no longer Markovian around the environment reset.
    """

    def __init__(
        self, env: ParallelEnv[AgentID, ObsType, ActionType], num_episodes: int
    ):
        """__init__.

        Args:
            env (AECEnv): the base environment
            num_episodes (int): the number of episodes to run the underlying environment
        """
        super().__init__(env)
        assert isinstance(env, ParallelEnv), (
            "MultiEpisodeEnv is only compatible with ParallelEnv environments."
        )

        self._num_episodes = num_episodes

    @override
    def reset(
        self, seed: int | None = None, options: dict[str, Any] | None = None
    ) -> tuple[dict[AgentID, ObsType], dict[AgentID, dict[str, Any]]]:
        """Reset the environment and the episode counter.

        Args:
            seed (int | None): seed for resetting the environment
            options (dict | None): options

        Returns:
            tuple[dict[AgentID, ObsType], dict[AgentID, dict]]:
        """
        obs, info = super().reset(seed=seed, options=options)

        self._seed = copy.deepcopy(seed)
        self._options = copy.deepcopy(options)
        self._episodes_elapsed = 1

        return obs, info

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
        """Steps the environment.

        When there are no more valid agents in the underlying environment, the environment is automatically reset.
        When this happens, the `observation` and `info` returned by `step()` are replaced with that of the reset environment.
        The result of this wrapper is that the environment is no longer Markovian around the environment reset.

        Args:
            actions (dict[AgentID, ActionType]): dictionary mapping of `AgentID`s to actions

        Returns:
            tuple[
                dict[AgentID, ObsType],
                dict[AgentID, float],
                dict[AgentID, bool],
                dict[AgentID, bool],
                dict[AgentID, dict],
            ]:
        """
        obs, rew, term, trunc, info = super().step(actions)

        if self.agents:
            return obs, rew, term, trunc, info

        # override the term trunc to only trunc when num_episodes have been elapsed
        if self._episodes_elapsed >= self._num_episodes:
            term = dict.fromkeys(self.agents, False)
            trunc = dict.fromkeys(self.agents, True)
            return obs, rew, term, trunc, info

        # if any agent terminates or truncates
        # and we haven't elapsed `num_episodes`
        # reset the environment
        # the observation and info are replaced with the new episode's, while the
        # rewards and flags still describe the episode that just finished; entries
        # are kept for both the finished and the new agent sets so the tuple is
        # keyed to a single consistent key set
        # the result is that this env is no longer Markovian at the reset points
        self._episodes_elapsed += 1
        self._seed = self._seed + 1 if self._seed else None
        obs, info = super().reset(seed=self._seed, options=self._options)
        rew = {**dict.fromkeys(self.agents, 0.0), **rew}
        term = {**dict.fromkeys(self.agents, False), **term}
        trunc = {**dict.fromkeys(self.agents, False), **trunc}
        return obs, rew, term, trunc, info
