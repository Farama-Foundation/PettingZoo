from pettingzoo.classic import (
    chess_v6,
    connect_four_v3,
    gin_rummy_v4,
    go_v5,
    hanabi_v5,
    leduc_holdem_v4,
    rps_v2,
    texas_holdem_no_limit_v6,
    texas_holdem_v4,
    tictactoe_v3,
)
from pettingzoo.utils.deprecated_module import deprecated_handler

classic_environments = {
    "chess_v6": chess_v6,
    "rps_v2": rps_v2,
    "connect_four_v3": connect_four_v3,
    "tictactoe_v3": tictactoe_v3,
    "leduc_holdem_v4": leduc_holdem_v4,
    "texas_holdem_v4": texas_holdem_v4,
    "texas_holdem_no_limit_v6": texas_holdem_no_limit_v6,
    "gin_rummy_v4": gin_rummy_v4,
    "go_v5": go_v5,
    "hanabi_v5": hanabi_v5,
}


def __getattr__(env_name):
    return deprecated_handler(env_name, __path__, __name__)
