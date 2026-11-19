import warnings

from pettingzoo.butterfly.knights_archers_zombies.knights_archers_zombies import (
    env,
    parallel_env,
    raw_env,
)
from pettingzoo.butterfly.knights_archers_zombies.manual_policy import ManualPolicy
from pettingzoo.utils.deprecated_module import CREATE_ENV_WITHOUT_REGISTRY

warnings.warn(CREATE_ENV_WITHOUT_REGISTRY, DeprecationWarning, stacklevel=2)

__all__ = ["ManualPolicy", "env", "parallel_env", "raw_env"]
