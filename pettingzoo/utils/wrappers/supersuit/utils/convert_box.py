from gymnasium.spaces import Box
from typing import Callable


def convert_box(convert_obs_fn: Callable, old_box: Box) -> Box:
    """
    Convert the bounds of a Box object using a given conversion function.

    Args:
        convert_obs_fn (Callable): A function that takes an ndarray and returns a transformed ndarray.
        old_box (Box): The original Box object to be converted.

    Returns:
        Box: A new Box object with transformed lower and upper bounds based on the conversion function.

    Note:
        The `convert_obs_fn` should be a function that accepts and returns NumPy ndarrays of the same shape.
    """
    new_low = convert_obs_fn(old_box.low)
    new_high = convert_obs_fn(old_box.high)
    return Box(low=new_low, high=new_high, dtype=new_low.dtype)
