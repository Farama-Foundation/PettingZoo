from pettingzoo.sisl import multiwalker_v9, pursuit_v4, waterworld_v4
from pettingzoo.utils.deprecated_module import deprecated_handler

sisl_environments = {
    "multiwalker_v9": multiwalker_v9,
    "waterworld_v4": waterworld_v4,
    "pursuit_v4": pursuit_v4,
}


def __getattr__(env_name):
    return deprecated_handler(env_name, __path__, __name__)
