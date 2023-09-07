import warnings
from collections import defaultdict


def make_defaultdict(d: dict) -> defaultdict:
    """
    Create a defaultdict with the same types as the input dictionary or return an empty dictionary.

    Args:
        d (dict): The input dictionary.

    Returns:
        defaultdict: A defaultdict with the same types as the input dictionary.

    Note:
        If the input dictionary is empty, a warning is issued, and an empty dictionary is returned.
    """
    try:
        dd = defaultdict(type(next(iter(d.values()))))
        for k, v in d.items():
            dd[k] = v
        return dd
    except StopIteration:
        warnings.warn("No agents left in the environment!")
        return {}
