import warnings

from pettingzoo.atari.entombed_cooperative.entombed_cooperative import (
    env,
    parallel_env,
    raw_env,
)
from pettingzoo.utils.deprecated_module import CREATE_ENV_WITHOUT_REGISTRY

warnings.warn(CREATE_ENV_WITHOUT_REGISTRY, DeprecationWarning, stacklevel=2)

__all__ = ["env", "parallel_env", "raw_env"]
