import warnings

from pettingzoo.classic.rlcard_envs.texas_holdem_no_limit import env, raw_env
from pettingzoo.utils.deprecated_module import CREATE_ENV_WITHOUT_REGISTRY

warnings.warn(CREATE_ENV_WITHOUT_REGISTRY, DeprecationWarning, stacklevel=2)

__all__ = ["env", "raw_env"]
