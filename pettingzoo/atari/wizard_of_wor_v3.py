import warnings

from pettingzoo.atari.wizard_of_wor.wizard_of_wor import env, parallel_env, raw_env
from pettingzoo.utils.deprecated_module import CREATE_ENV_WITHOUT_REGISTRY

warnings.warn(CREATE_ENV_WITHOUT_REGISTRY, DeprecationWarning, stacklevel=2)

__all__ = ["env", "parallel_env", "raw_env"]
