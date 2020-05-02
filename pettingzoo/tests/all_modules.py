from pettingzoo.classic import chess_v0
from pettingzoo.classic import rps_v0
from pettingzoo.classic import rpsls_v0
from pettingzoo.classic import connect_four_v0
from pettingzoo.classic import tictactoe_v0
from pettingzoo.classic import leduc_holdem_v0
from pettingzoo.classic import mahjong_v0
from pettingzoo.classic import texas_holdem_v0
from pettingzoo.classic import texas_holdem_no_limit_v0
from pettingzoo.classic import uno_v0
from pettingzoo.classic import dou_dizhu_v0
from pettingzoo.classic import gin_rummy_v0
from pettingzoo.classic import go_v0

from pettingzoo.gamma import knights_archers_zombies_v0
from pettingzoo.gamma import pistonball_v0
from pettingzoo.gamma import cooperative_pong_v0
from pettingzoo.gamma import prison_v0

from pettingzoo.mpe import simple_adversary_v0
from pettingzoo.mpe import simple_crypto_v0
from pettingzoo.mpe import simple_push_v0
from pettingzoo.mpe import simple_reference_v0
from pettingzoo.mpe import simple_speaker_listener_v0
from pettingzoo.mpe import simple_spread_v0
from pettingzoo.mpe import simple_tag_v0
from pettingzoo.mpe import simple_world_comm_v0
from pettingzoo.mpe import simple_v0

from pettingzoo.sisl import pursuit_v0
from pettingzoo.sisl import waterworld_v0
from pettingzoo.sisl import multiwalker_v0

all_environments = {
    "classic/chess": chess_v0,
    "classic/rps": rps_v0,
    "classic/rpsls": rpsls_v0,
    "classic/connect_four": connect_four_v0,
    "classic/tictactoe": tictactoe_v0,
    "classic/leduc_holdem": leduc_holdem_v0,
    "classic/mahjong": mahjong_v0,
    "classic/texas_holdem": texas_holdem_v0,
    "classic/texas_holdem_no_limit": texas_holdem_no_limit_v0,
    "classic/uno": uno_v0,
    "classic/dou_dizhu": dou_dizhu_v0,
    "classic/gin_rummy": gin_rummy_v0,
    "classic/go": go_v0,

    "gamma/knights_archers_zombies": knights_archers_zombies_v0,
    "gamma/pistonball": pistonball_v0,
    "gamma/cooperative_pong": cooperative_pong_v0,
    "gamma/prison": prison_v0,

    "mpe/simple_adversary": simple_adversary_v0,
    "mpe/simple_crypto": simple_crypto_v0,
    "mpe/simple_push": simple_push_v0,
    "mpe/simple_reference": simple_reference_v0,
    "mpe/simple_speaker_listener": simple_speaker_listener_v0,
    "mpe/simple_spread": simple_spread_v0,
    "mpe/simple_tag": simple_tag_v0,
    "mpe/simple_world_comm": simple_world_comm_v0,
    "mpe/simple": simple_v0,

    "sisl/multiwalker": multiwalker_v0,
    "sisl/waterworld": waterworld_v0,
    "sisl/pursuit": pursuit_v0,
}
