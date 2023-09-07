from utils.base_aec_wrapper import PettingzooWrap
from utils.make_defaultdict import make_defaultdict
from typing import Callable
from pettingzoo import AECEnv, ParallelEnv
from pettingzoo.utils.env import ActionType


class AecRewardLambda(PettingzooWrap):
    """
    A wrapper for AEC environments that allows the modification of rewards.

    Args:
        env (AECEnv | ParallelEnv): The environment to be wrapped.
        change_reward_fn (Callable): A function that modifies rewards.

    Raises:
        AssertionError: If `change_reward_fn` is not callable.

    Attributes:
        _change_reward_fn (Callable): The function used to modify rewards.

    Methods:
        reset(seed: int = None, options: dict = None) -> None:
            Reset the environment, applying the reward modification to initial rewards.

        step(action: ActionType) -> None:
            Take a step in the environment, applying the reward modification to the received rewards.

    """
    def __init__(self, env: AECEnv | ParallelEnv, change_reward_fn: Callable):
        assert callable(
            change_reward_fn
        ), f"change_reward_fn needs to be a function. It is {change_reward_fn}"
        self._change_reward_fn = change_reward_fn

        super().__init__(env)

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

    def reset(self, seed: int = None, options: dict = None) -> None:
        """
        Reset the environment, applying the reward modification to initial rewards.

        Args:
            seed (int, optional): A seed for environment randomization. Default is None.
            options (dict, optional): Additional options for environment initialization. Default is None.
        """
        super().reset(seed=seed, options=options)
        self.rewards = {
            agent: self._change_reward_fn(reward)
            for agent, reward in self.rewards.items()
        }
        self.__cumulative_rewards = make_defaultdict({a: 0 for a in self.agents})
        self._accumulate_rewards()

    def step(self, action: ActionType) -> None:
        """
        Take a step in the environment, applying the reward modification to the received rewards.

        Args:
            action (ActionType): The action to be taken in the environment.
        """
        agent = self.env.agent_selection
        super().step(action)
        self.rewards = {
            agent: self._change_reward_fn(reward)
            for agent, reward in self.rewards.items()
        }
        self.__cumulative_rewards[agent] = 0
        self._cumulative_rewards = self.__cumulative_rewards
        self._accumulate_rewards()


reward_lambda_v0 = AecRewardLambda
""" example:
reward_lambda_v0 = WrapperChooser(
    aec_wrapper=AecRewardLambda, par_wrapper=ParRewardLambda
)"""
