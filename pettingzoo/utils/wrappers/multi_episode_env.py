from __future__ import annotations

import copy

from pettingzoo.utils.env import ActionType, AECEnv
from pettingzoo.utils.wrappers.base import BaseWrapper


class MultiEpisodeEnv(BaseWrapper):
    """Creates a new environment using the base environment that runs for `num_episodes` before truncating.

    This is useful for creating evaluation environments.
    When there are no more valid agents in the underlying environment, the environment is automatically reset.
    After `num_episodes` have been run internally, the environment terminates normally.
    The result of this wrapper is that the environment is no longer Markovian around the environment reset.

    When `starting_utility` is used, all agents start with a base amount of health points (think of this as poker chips).
    Whenever the agent gets a negative reward, this value is subtracted from starting utility.
    Whenever the agent gets a positive reward, it is added to the starting utility.
    Agents which run out of starting utility are terminated.
    """

    def __init__(
        self, env: AECEnv, num_episodes: int, starting_utility: float | None = None
    ):
        """__init__.

        Args:
            env (AECEnv): env
            num_episodes (int): num_episodes
            starting_utility (Optional[float]): starting_utility
        """
        assert isinstance(
            env, AECEnv
        ), "MultiEpisodeEnv is only compatible with AEC environments"
        super().__init__(env)

        self._num_episodes = num_episodes
        self._starting_utility = starting_utility

    def reset(self, seed: int | None = None, options: dict | None = None) -> None:
        """reset.

        Args:
            seed (int | None): seed
            options (dict | None): options

        Returns:
            None:
        """
        super().reset(seed=seed, options=options)
        self._episodes_elapsed = 1
        self._seed = copy.deepcopy(seed)
        self._options = copy.deepcopy(options)
        if self._starting_utility:
            self._agent_utilities = {a: self._starting_utility for a in self.agents}

    def step(self, action: ActionType) -> None:
        """Steps the underlying environment for `num_episodes`.

        This is useful for creating evaluation environments.
        When there are no more valid agents in the underlying environment, the environment is automatically reset.
        After `num_episodes` have been run internally, the environment terminates normally.
        The result of this wrapper is that the environment is no longer Markovian around the environment reset.

        Args:
            action (ActionType): action

        Returns:
            None:
        """
        super().step(action)

        # adjust utilities if this param is enabled
        if self._starting_utility:
            for agent in self.agents:
                self._agent_utilities[agent] = (
                    self._agent_utilities[agent] + self.rewards[agent]
                )

                if self._agent_utilities[agent] <= 0:
                    self.terminations[agent] = True

        # if we still have agents, don't need to do anything
        if self.agents:
            return

        # if we've crossed num_episodes, truncate all agents
        # and let the environment terminate normally
        if self._episodes_elapsed >= self._num_episodes:
            self.truncations = {agent: True for agent in self.agents}
            return

        # if no more agents and haven't had enough episodes,
        # increment the number of episodes and the seed for reset
        self._episodes_elapsed += 1
        self._seed = self._seed + 1 if self._seed else None
        super().reset(seed=self._seed, options=self._options)
        self.truncations = {agent: False for agent in self.agents}
        self.terminations = {agent: False for agent in self.agents}

    def __str__(self) -> str:
        """__str__.

        Args:

        Returns:
            str:
        """
        return str(self.env)
