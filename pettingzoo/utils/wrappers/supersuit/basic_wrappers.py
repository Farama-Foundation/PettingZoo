from reward_lambda import reward_lambda_v0, AecRewardLambda
from observation_lambda import observation_lambda_v0, AecObservationLambda
from utils.basic_transforms import color_reduction
from typing import Literal, Any
from types import ModuleType
from pettingzoo import AECEnv, ParallelEnv
from gymnasium.spaces import Space
import numpy as np


def basic_obs_wrapper(env: AECEnv | ParallelEnv, module: ModuleType, param: Any) -> AecObservationLambda:
    """
    Wrap an environment to modify its observation space and observations using a specified module and parameter.

    This function takes an environment, a module, and a parameter, and creates a new environment with an observation
    space and observations modified based on the provided module and parameter.

    Parameters:
    - env (Generic[AgentID, ObsType, ActionType]): The environment to be wrapped.
    - module: The module responsible for modifying the observation space and observations.
    - param: The parameter used to modify the observation space and observations.

    Returns:
    - AecObservationLambda: A wrapped environment that applies the observation space and observation modifications. #TODO fix this line

    Example:
    ```python
    modified_env = basic_obs_wrapper(original_env, my_module, my_param)
    ```
    In the above example, `modified_env` is a new environment that has its observation space and observations modified
    according to the `my_module` and `my_param`.
    """

    def change_space(space: Space):  # Box?
        module.check_param(space, param)
        space = module.change_obs_space(space, param)
        return space

    def change_obs(obs: np.ndarray, obs_space: Space):  # not sure about ndarray
        return module.change_observation(obs, obs_space, param)

    return observation_lambda_v0(env, change_obs, change_space)


def color_reduction_v0(env: AECEnv | ParallelEnv, mode: Literal["full", "R", "G", "B"] = "full") -> AecObservationLambda:
    """
   Wrap an environment to perform color reduction on its observations.

   This function takes an environment and an optional mode to specify the color reduction technique. It then creates
   a new environment that performs color reduction on the observations based on the specified mode.

   Parameters:
   - env (Generic[AgentID, ObsType, ActionType]): The environment to be wrapped.
   - mode (Union[str, color_reduction.COLOR_RED_LIST], optional): The color reduction mode to apply (default is "full").
     Valid modes are defined in the color_reduction module.

   Returns:
   - AecObservationLambda: A wrapped environment that applies color reduction to its observations. #TODO fix this line

   Example:
   ```python
   reduced_color_env = color_reduction_v0(original_env, mode="grayscale")
   ```
   In the above example, `reduced_color_env` is a new environment that performs grayscale color reduction on its
   observations.
   """

    return basic_obs_wrapper(env, color_reduction, mode)


def clip_reward_v0(env: AECEnv | ParallelEnv, lower_bound: float = -1, upper_bound: float = 1) -> AecRewardLambda:
    """
    Clip rewards in an environment using the specified lower and upper bounds.

    This function applies a reward clipping transformation to an environment's rewards. It takes an environment and
    two optional bounds: `lower_bound` and `upper_bound`. Any reward in the environment that falls below the
    `lower_bound` will be set to `lower_bound`, and any reward that exceeds the `upper_bound` will be set to
    `upper_bound`. Rewards within the specified range are left unchanged.

    Parameters:
    - env (Generic[AgentID, ObsType, ActionType]): The environment on which to apply the reward clipping.
    - lower_bound (float, optional): The lower bound for clipping rewards (default is -1).
    - upper_bound (float, optional): The upper bound for clipping rewards (default is 1).

    Returns:
    - AecRewardLambda: A reward transformation function that applies the specified reward clipping when called. #TODO fix this line

    Example:
    ```python
    clipped_env = clip_reward_v0(my_environment, lower_bound=-0.5, upper_bound=0.5)
    ```
    In the above example, the rewards in `my_environment` will be clipped to the range [-0.5, 0.5].
    """

    return reward_lambda_v0(env, lambda rew: max(min(rew, upper_bound), lower_bound))
