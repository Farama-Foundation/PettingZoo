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

classic_environments = {
    "classic/chess_v6": chess_v6,
    "classic/rps_v2": rps_v2,
    "classic/connect_four_v3": connect_four_v3,
    "classic/tictactoe_v3": tictactoe_v3,
    "classic/leduc_holdem_v4": leduc_holdem_v4,
    "classic/texas_holdem_v4": texas_holdem_v4,
    "classic/texas_holdem_no_limit_v6": texas_holdem_no_limit_v6,
    "classic/gin_rummy_v4": gin_rummy_v4,
    "classic/go_v5": go_v5,
    "classic/hanabi_v5": hanabi_v5,
}
