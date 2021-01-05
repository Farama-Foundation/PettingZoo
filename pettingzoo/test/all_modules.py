from pettingzoo.atari import basketball_pong_v1
from pettingzoo.atari import boxing_v1
from pettingzoo.atari import combat_plane_v1
from pettingzoo.atari import combat_tank_v1
from pettingzoo.atari import double_dunk_v2
from pettingzoo.atari import entombed_competitive_v2
from pettingzoo.atari import entombed_cooperative_v2
from pettingzoo.atari import flag_capture_v1
from pettingzoo.atari import foozpong_v1
from pettingzoo.atari import ice_hockey_v1
from pettingzoo.atari import joust_v2
from pettingzoo.atari import mario_bros_v2
from pettingzoo.atari import maze_craze_v2
from pettingzoo.atari import othello_v2
from pettingzoo.atari import pong_v1
from pettingzoo.atari import quadrapong_v2
from pettingzoo.atari import space_invaders_v1
from pettingzoo.atari import space_war_v1
from pettingzoo.atari import surround_v1
from pettingzoo.atari import tennis_v2
from pettingzoo.atari import video_checkers_v3
from pettingzoo.atari import volleyball_pong_v1
from pettingzoo.atari import wizard_of_wor_v2
from pettingzoo.atari import warlords_v2

from pettingzoo.classic import chess_v2
from pettingzoo.classic import checkers_v2
from pettingzoo.classic import rps_v1
from pettingzoo.classic import rpsls_v1
from pettingzoo.classic import connect_four_v2
from pettingzoo.classic import tictactoe_v2
from pettingzoo.classic import leduc_holdem_v2
from pettingzoo.classic import mahjong_v2
from pettingzoo.classic import texas_holdem_v2
from pettingzoo.classic import texas_holdem_no_limit_v2
from pettingzoo.classic import uno_v2
from pettingzoo.classic import dou_dizhu_v2
from pettingzoo.classic import gin_rummy_v2
from pettingzoo.classic import go_v2
from pettingzoo.classic import hanabi_v3
from pettingzoo.classic import backgammon_v2

from pettingzoo.butterfly import knights_archers_zombies_v5
from pettingzoo.butterfly import pistonball_v3
from pettingzoo.butterfly import cooperative_pong_v2
from pettingzoo.butterfly import prison_v2
from pettingzoo.butterfly import prospector_v3

from pettingzoo.magent import battle_v2
from pettingzoo.magent import adversarial_pursuit_v2
from pettingzoo.magent import gather_v2
from pettingzoo.magent import combined_arms_v3
from pettingzoo.magent import tiger_deer_v3
from pettingzoo.magent import battlefield_v2

from pettingzoo.mpe import simple_adversary_v2
from pettingzoo.mpe import simple_crypto_v2
from pettingzoo.mpe import simple_push_v2
from pettingzoo.mpe import simple_reference_v2
from pettingzoo.mpe import simple_speaker_listener_v3
from pettingzoo.mpe import simple_spread_v2
from pettingzoo.mpe import simple_tag_v2
from pettingzoo.mpe import simple_world_comm_v2
from pettingzoo.mpe import simple_v2

from pettingzoo.sisl import pursuit_v3
from pettingzoo.sisl import waterworld_v3
from pettingzoo.sisl import multiwalker_v6

all_prefixes = ["atari", "classic", "butterfly", "magent", "mpe", "sisl"]

manual_environments = {
    "butterfly/knights_archers_zombies",
    "butterfly/pistonball",
    "butterfly/cooperative_pong",
    "butterfly/prison",
    "butterfly/prospector",
    "sisl/pursuit"
}

all_environments = {
    "atari/basketball_pong": basketball_pong_v1,
    "atari/boxing": boxing_v1,
    "atari/combat_tank": combat_tank_v1,
    "atari/combat_plane": combat_plane_v1,
    "atari/double_dunk": double_dunk_v2,
    "atari/entombed_cooperative": entombed_cooperative_v2,
    "atari/entombed_competitive": entombed_competitive_v2,
    "atari/flag_capture": flag_capture_v1,
    "atari/foozpong": foozpong_v1,
    "atari/joust": joust_v2,
    "atari/ice_hockey": ice_hockey_v1,
    "atari/maze_craze": maze_craze_v2,
    "atari/mario_bros": mario_bros_v2,
    "atari/othello": othello_v2,
    "atari/pong": pong_v1,
    "atari/quadrapong": quadrapong_v2,
    "atari/space_invaders": space_invaders_v1,
    "atari/space_war": space_war_v1,
    "atari/surround": surround_v1,
    "atari/tennis": tennis_v2,
    "atari/video_checkers": video_checkers_v3,
    "atari/volleyball_pong": volleyball_pong_v1,
    "atari/wizard_of_wor": wizard_of_wor_v2,
    "atari/warlords": warlords_v2,

    "classic/chess": chess_v2,
    "classic/checkers": checkers_v2,
    "classic/rps": rps_v1,
    "classic/rpsls": rpsls_v1,
    "classic/connect_four": connect_four_v2,
    "classic/tictactoe": tictactoe_v2,
    "classic/leduc_holdem": leduc_holdem_v2,
    "classic/mahjong": mahjong_v2,
    "classic/texas_holdem": texas_holdem_v2,
    "classic/texas_holdem_no_limit": texas_holdem_no_limit_v2,
    "classic/uno": uno_v2,
    "classic/dou_dizhu": dou_dizhu_v2,
    "classic/gin_rummy": gin_rummy_v2,
    "classic/go": go_v2,
    "classic/hanabi": hanabi_v3,
    "classic/backgammon": backgammon_v2,

    "butterfly/knights_archers_zombies": knights_archers_zombies_v5,
    "butterfly/pistonball": pistonball_v3,
    "butterfly/cooperative_pong": cooperative_pong_v2,
    "butterfly/prison": prison_v2,
    "butterfly/prospector": prospector_v3,

    # "magent/adversarial_pursuit": adversarial_pursuit_v2,
    # "magent/battle": battle_v2,
    # "magent/battlefield": battlefield_v2,
    # "magent/combined_arms": combined_arms_v3,
    # "magent/gather": gather_v2,
    # "magent/tiger_deer": tiger_deer_v3,

    "mpe/simple_adversary": simple_adversary_v2,
    "mpe/simple_crypto": simple_crypto_v2,
    "mpe/simple_push": simple_push_v2,
    "mpe/simple_reference": simple_reference_v2,
    "mpe/simple_speaker_listener": simple_speaker_listener_v3,
    "mpe/simple_spread": simple_spread_v2,
    "mpe/simple_tag": simple_tag_v2,
    "mpe/simple_world_comm": simple_world_comm_v2,
    "mpe/simple": simple_v2,

    "sisl/multiwalker": multiwalker_v6,
    "sisl/waterworld": waterworld_v3,
    "sisl/pursuit": pursuit_v3,
}
