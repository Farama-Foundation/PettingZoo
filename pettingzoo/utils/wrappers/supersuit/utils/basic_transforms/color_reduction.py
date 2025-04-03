import numpy as np
from pettingzoo.utils.wrappers.supersuit.utils.convert_box import convert_box
from gymnasium.spaces import Box


COLOR_RED_LIST = ["full", "R", "G", "B"]
GRAYSCALE_WEIGHTS = np.array([0.299, 0.587, 0.114], dtype=np.float32)


def check_param(space: Box, color_reduction: str) -> None:
    """
    Check if the provided parameters are valid for color reduction. #TODO fix this line

    Args:
        space (Box): The observation space as a Box object.
        color_reduction (str): The desired color reduction method.

    Raises:
        AssertionError: If the color_reduction is not a string or is not in the COLOR_RED_LIST,
                        or if the shape of the space is not a 3D image with the last dimension
                        having a size of 3.
    """
    assert isinstance(
        color_reduction, str
    ), f"color_reduction must be str. It is {color_reduction}"
    assert color_reduction in COLOR_RED_LIST, "color_reduction must be in {}".format(
        COLOR_RED_LIST
    )
    assert (
        len(space.low.shape) == 3 and space.low.shape[2] == 3
    ), "To apply color_reduction, shape must be a 3d image with last dimension of size 3. Shape is {}".format(
        space.low.shape
    )


def change_obs_space(obs_space: Box, param: str) -> Box:
    """
    Change the observation space based on a color reduction parameter.  #TODO fix this line

    Args:
        obs_space (Box): The original observation space as a Box object.
        param (str): The color reduction parameter.

    Returns:
        Box: The modified observation space.
    """
    return convert_box(lambda obs: change_observation(obs, obs_space, param), obs_space)


def change_observation(obs: np.ndarray, obs_space: Box, color_reduction: str) -> np.ndarray:
    """
    Apply color reduction to an observation based on the specified color_reduction parameter.  #TODO fix this line

    Args:
        obs (np.ndarray): The input observation as a NumPy array.
        obs_space (Box): The original observation space as a Box object.
        color_reduction (str): The color reduction method to be applied.

    Returns:
        np.ndarray: The modified observation after applying color reduction.
    """
    if color_reduction == "R":
        obs = obs[:, :, 0]
    if color_reduction == "G":
        obs = obs[:, :, 1]
    if color_reduction == "B":
        obs = obs[:, :, 2]
    if color_reduction == "full":
        obs = (obs.astype(np.float32) @ GRAYSCALE_WEIGHTS).astype(np.uint8)
    return obs
