import warnings

from pettingzoo.butterfly.pistonball.pistonball import (
    ManualPolicy,
    env,
    parallel_env,
    raw_env,
)
from pettingzoo.utils.deprecated_module import CREATE_ENV_WITHOUT_REGISTRY

warnings.warn(CREATE_ENV_WITHOUT_REGISTRY, DeprecationWarning, stacklevel=2)

__all__ = ["ManualPolicy", "env", "parallel_env", "raw_env"]
