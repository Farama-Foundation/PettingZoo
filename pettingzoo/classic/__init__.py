from pettingzoo.utils.deprecated_module import depricated_handler


def __getattr__(env_name):
    return depricated_handler(env_name, __path__, __name__)
