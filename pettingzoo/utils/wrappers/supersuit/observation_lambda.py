import functools
import numpy as np
from gymnasium.spaces import Box, Discrete
from utils.base_aec_wrapper import BaseWrapper
from typing import Callable
from pettingzoo import AECEnv, ParallelEnv
from pettingzoo.utils.env import ActionType, AgentID


class AecObservationLambda(BaseWrapper):
    """
    A wrapper for AEC environments that allows the modification of observation spaces and observations.

    Args:
        env (AECEnv | ParallelEnv): The environment to be wrapped.
        change_observation_fn (Callable): A function that modifies observations.
        change_obs_space_fn (Callable, optional): A function that modifies observation spaces. Default is None.

    Raises:
        AssertionError: If `change_observation_fn` is not callable, or if `change_obs_space_fn` is provided and is not callable.

    Note:
        - The `change_observation_fn` should be a function that accepts observation data and optionally the observation space and agent ID as arguments and returns a modified observation.
        - The `change_obs_space_fn` should be a function that accepts an old observation space and optionally the agent ID as arguments and returns a modified observation space.

    Attributes:
        change_observation_fn (Callable): The function used to modify observations.
        change_obs_space_fn (Callable, optional): The function used to modify observation spaces.

    Methods:
        _modify_action(agent: str, action: Discrete) -> Discrete:
            Modify the action.

        _check_wrapper_params() -> None:
            Check wrapper parameters for consistency.

        observation_space(agent: str) -> Box:
            Get the modified observation space for a specific agent.

        _modify_observation(agent: str, observation: Box) -> Box:
            Modify the observation.

    """
    def __init__(self, env: AECEnv | ParallelEnv, change_observation_fn: Callable, change_obs_space_fn: Callable = None):
        assert callable(
            change_observation_fn
        ), "change_observation_fn needs to be a function. It is {}".format(
            change_observation_fn
        )
        assert change_obs_space_fn is None or callable(
            change_obs_space_fn
        ), "change_obs_space_fn needs to be a function. It is {}".format(
            change_obs_space_fn
        )

        self.change_observation_fn = change_observation_fn
        self.change_obs_space_fn = change_obs_space_fn

        super().__init__(env)

        if hasattr(self, "possible_agents"):
            for agent in self.possible_agents:
                # call any validation logic in this function
                self.observation_space(agent)

    def _modify_action(self, agent: AgentID, action: ActionType) -> ActionType:
        """
        Modify the action.

        Args:
            agent (str): The agent for which to modify the action.
            action (Discrete): The original action.

        Returns:
            Discrete: The modified action.
        """
        return action

    def _check_wrapper_params(self) -> None:
        """
        Check wrapper parameters for consistency.

        Raises:
            AssertionError: If the provided parameters are inconsistent.
        """
        if self.change_obs_space_fn is None and hasattr(self, "possible_agents"):
            for agent in self.possible_agents:
                assert isinstance(
                    self.observation_space(agent), Box
                ), "the observation_lambda_wrapper only allows the change_obs_space_fn argument to be optional for Box observation spaces"

    @functools.lru_cache(maxsize=None)
    def observation_space(self, agent: AgentID) -> Box:
        """
        Get the modified observation space for a specific agent.

        Args:
            agent (str): The agent for which to retrieve the observation space.

        Returns:
            Box: The modified observation space.
        """
        if self.change_obs_space_fn is None:
            space = self.env.observation_space(agent)
            try:
                trans_low = self.change_observation_fn(space.low, space, agent)
                trans_high = self.change_observation_fn(space.high, space, agent)
            except TypeError:
                trans_low = self.change_observation_fn(space.low, space)
                trans_high = self.change_observation_fn(space.high, space)
            new_low = np.minimum(trans_low, trans_high)
            new_high = np.maximum(trans_low, trans_high)

            return Box(low=new_low, high=new_high, dtype=new_low.dtype)
        else:
            old_obs_space = self.env.observation_space(agent)
            try:
                return self.change_obs_space_fn(old_obs_space, agent)
            except TypeError:
                return self.change_obs_space_fn(old_obs_space)

    def _modify_observation(self, agent: AgentID, observation: Box) -> Box:
        """
        Modify the observation.

        Args:
            agent (str): The agent for which to modify the observation.
            observation (Box): The original observation.

        Returns:
            Box: The modified observation.
        """
        old_obs_space = self.env.observation_space(agent)
        try:
            return self.change_observation_fn(observation, old_obs_space, agent)
        except TypeError:
            return self.change_observation_fn(observation, old_obs_space)


observation_lambda_v0 = AecObservationLambda
