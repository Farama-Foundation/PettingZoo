from pettingzoo.utils.deprecated_module import deprecated_handler


def __getattr__(env_name):
    return deprecated_handler(env_name, __path__, __name__)


# TODO: in a future release, remove all the MPE environments and uncomment the following lines to raise a warning
# instead of importing the environments
