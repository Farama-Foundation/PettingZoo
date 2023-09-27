from __future__ import annotations

import copy

from pettingzoo.utils.env import ActionType, AgentID, ObsType, ParallelEnv
from pettingzoo.utils.wrappers.base_parallel import BaseParallelWrapper


class MultiEpisodeParallelEnv(BaseParallelWrapper):
    """Creates a new environment using the base environment that runs for `num_episodes` before truncating.

    This is useful for creating evaluation environments.
    When there are no more valid agents in the underlying environment, the environment is automatically reset.
    When this happens, the `observation` and `info` returned by `step()` are replaced with that of the reset environment.
    The result of this wrapper is that the environment is no longer Markovian around the environment reset.

    When `starting_utility` is used, all agents start with a base amount of health points (think of this as poker chips).
    Whenever the agent gets a negative reward, this value is subtracted from starting utility.
    Whenever the agent gets a positive reward, it is added to the starting utility.
    Agents which run out of starting utility are terminated.
    """

    def __init__(
        self, env: ParallelEnv, num_episodes: int, starting_utility: float | None = None
    ):
        """__init__.

        Args:
            env (AECEnv): the base environment
            num_episodes (int): the number of episodes to run the underlying environment
            starting_utility (float | None): starting_utility
        """
        super().__init__(env)
        assert isinstance(
            env, ParallelEnv
        ), "MultiEpisodeEnv is only compatible with ParallelEnv environments."

        self._num_episodes = num_episodes
        self._starting_utility = starting_utility

    def reset(
        self, seed: int | None = None, options: dict | None = None
    ) -> tuple[dict[AgentID, ObsType], dict[AgentID, dict]]:
        """reset.

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
        if self._starting_utility:
            self._agent_utilities = {a: self._starting_utility for a in self.agents}

        return obs, info

    def step(
        self, actions: dict[AgentID, ActionType]
    ) -> tuple[
        dict[AgentID, ObsType],
        dict[AgentID, float],
        dict[AgentID, bool],
        dict[AgentID, bool],
        dict[AgentID, dict],
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

        # handle agent utilities if any
        if self._starting_utility:
            self._agent_utilities = {
                u[a] - r[a] for u, r, a in zip(self._agent_utilities, rew, self.agents)
            }
            # termination only depends on available utility now
            term = {agent: u <= 0 for agent, u in zip(term, self._agent_utilities)}
        else:
            term = {agent: False for agent in term}

        trunc = {agent: False for agent in term}

        if self.agents:
            return obs, rew, term, trunc, info

        # override the term trunc to only trunc when num_episodes have been elapsed
        if self._episodes_elapsed >= self._num_episodes:
            term = {agent: False for agent in term}
            trunc = {agent: True for agent in term}
            return obs, rew, term, trunc, info

        # if any agent terminates or truncates
        # and we haven't elapsed `num_episodes`
        # reset the environment
        # we also override the observation and infos
        # the result is that this env is no longer Markovian
        # at the reset points
        # increment the number of episodes and the seed for reset
        self._episodes_elapsed += 1
        self._seed = self._seed + 1 if self._seed else None
        obs, info = super().reset(seed=self._seed, options=self._options)
        return obs, rew, term, trunc, info
