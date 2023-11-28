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
    """

    def __init__(self, env: AECEnv, num_episodes: int):
        """__init__.

        Args:
            env (AECEnv): env
            num_episodes (int): num_episodes
        """
        assert isinstance(
            env, AECEnv
        ), "MultiEpisodeEnv is only compatible with AEC environments"
        super().__init__(env)

        self._num_episodes = num_episodes

    def reset(self, seed: int | None = None, options: dict | None = None) -> None:
        """reset.

        Args:
            seed (int | None): seed
            options (dict | None): options

        Returns:
            None:
        """
        self._episodes_elapsed = 1
        self._seed = copy.deepcopy(seed)
        self._options = copy.deepcopy(options)
        super().reset(seed=seed, options=options)

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
        if self.env.agents:
            return

        # if we've crossed num_episodes, truncate all agents
        # and let the environment terminate normally
        if self._episodes_elapsed >= self._num_episodes:
            self.env.unwrapped.truncations = {agent: True for agent in self.env.agents}
            return

        # if no more agents and haven't had enough episodes,
        # increment the number of episodes and the seed for reset
        self._episodes_elapsed += 1
        self._seed = self._seed + 1 if self._seed else None
        super().reset(seed=self._seed, options=self._options)

    def __str__(self) -> str:
        """__str__.

        Args:

        Returns:
            str:
        """
        return str(self.env)
