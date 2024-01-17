from pettingzoo.butterfly import (
    cooperative_pong_v5,
    knights_archers_zombies_v10,
    pistonball_v6,
)
from pettingzoo.utils.deprecated_module import deprecated_handler

butterfly_environments = {
    "knights_archers_zombies_v10": knights_archers_zombies_v10,
    "pistonball_v6": pistonball_v6,
    "cooperative_pong_v5": cooperative_pong_v5,
}


def __getattr__(env_name):
    return deprecated_handler(env_name, __path__, __name__)
