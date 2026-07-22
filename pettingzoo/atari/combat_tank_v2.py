import warnings

from pettingzoo.atari.combat_tank.combat_tank import env, parallel_env, raw_env
from pettingzoo.utils.deprecated_module import CREATE_ENV_WITHOUT_REGISTRY

warnings.warn(CREATE_ENV_WITHOUT_REGISTRY, DeprecationWarning, stacklevel=2)

__all__ = ["env", "parallel_env", "raw_env"]
