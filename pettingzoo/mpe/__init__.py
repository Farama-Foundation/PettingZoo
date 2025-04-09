import warnings

from pettingzoo.utils.deprecated_module import deprecated_handler


def __getattr__(env_name):
    return deprecated_handler(env_name, __path__, __name__)


warnings.warn(
    "The environment `pettingzoo.mpe` has been moved to `mpe2` and will be removed in a future release."
    "Please update your imports.",
    DeprecationWarning,
    stacklevel=2,
)

# TODO: in a future release, remove all the MPE environments and uncomment the following lines to raise a warning
# instead of importing the environments
