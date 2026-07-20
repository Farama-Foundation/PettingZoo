import warnings

from pettingzoo.atari.volleyball_pong.volleyball_pong import env, parallel_env, raw_env
from pettingzoo.utils.deprecated_module import CREATE_ENV_WITHOUT_REGISTRY

warnings.warn(CREATE_ENV_WITHOUT_REGISTRY, DeprecationWarning, stacklevel=2)

__all__ = ["env", "parallel_env", "raw_env"]
