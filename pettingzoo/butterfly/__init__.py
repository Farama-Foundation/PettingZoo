from pettingzoo.utils.deprecated_module import deprecated_handler


def __getattr__(env_name):
    return deprecated_handler(env_name, __path__, __name__)
