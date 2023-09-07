from pettingzoo.utils.wrappers import OrderEnforcingWrapper as PettingzooWrap
from pettingzoo import AECEnv, ParallelEnv
from pettingzoo.utils.env import ActionType, AgentID
from gymnasium.spaces import Space


class BaseWrapper(PettingzooWrap):
    def __init__(self, env: AECEnv | ParallelEnv):
        """
        Creates a wrapper around `env`. Extend this class to create changes to the space.
        """
        super().__init__(env)

        self._check_wrapper_params()

        self._modify_spaces()

    def _check_wrapper_params(self) -> None:
        """
        Check wrapper parameters for consistency.

        This method is currently empty and does not perform any checks.
        """
        pass

    def _modify_spaces(self) -> None:
        """
        Modify the spaces of the wrapped environment.

        This method is currently empty and does not modify the spaces.
        """
        pass

    def _modify_action(self, agent: AgentID, action: ActionType) -> None:
        """
        Modify the action for the given agent.

        This method should be implemented by subclasses.

        Args:
            agent (AgentID): The agent for which to modify the action.
            action (ActionType): The original action to be modified.

        Raises:
            NotImplementedError: This method should be implemented in subclasses.
        """
        raise NotImplementedError()

    def _modify_observation(self, agent: AgentID, observation: Space) -> None:
        """
        Modify the observation for the given agent.

        This method should be implemented by subclasses.

        Args:
            agent (AgentID): The agent for which to modify the observation.
            observation (Space): The original observation to be modified.

        Raises:
            NotImplementedError: This method should be implemented in subclasses.
        """
        raise NotImplementedError()

    def _update_step(self, agent: AgentID) -> None:
        """
        Update the step for the given agent.

        This method can be implemented by subclasses if needed.

        Args:
            agent (AgentID): The agent for which to update the step.
        """
        pass

    def reset(self, seed: int = None, options: dict = None) -> None:
        """
        Reset the environment, optionally setting a seed and providing additional options.

        Args:
            seed (int, optional): A seed for environment randomization. Default is None.
            options (dict, optional): Additional options for environment initialization. Default is None.
        """
        super().reset(seed=seed, options=options)
        self._update_step(self.agent_selection)

    def observe(self, agent: AgentID) -> Space:
        """
        Observe the environment's state for the specified agent, modifying the observation if needed.

        Args:
            agent (AgentID): The agent for which to observe the environment.

        Returns:
            Space: The modified observation of the environment state for the specified agent.
        """
        obs = super().observe(
            agent
        )  # problem is in this line, the obs is sometimes a different size from the obs space
        observation = self._modify_observation(agent, obs)
        return observation

    def step(self, action: ActionType) -> None:
        """
        Take a step in the environment with the given action, modifying the action if required.

        Args:
            action (ActionType): The action to be taken in the environment.
        """
        agent = self.env.agent_selection
        if not self.terminations[agent] or self.truncations[agent]:
            action = self._modify_action(agent, action)

        super().step(action)

        self._update_step(self.agent_selection)
