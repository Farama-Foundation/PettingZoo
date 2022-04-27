from pettingzoo.atari import basketball_pong_v3
from pettingzoo.atari import boxing_v2
from pettingzoo.atari import combat_plane_v2
from pettingzoo.atari import combat_tank_v2
from pettingzoo.atari import double_dunk_v3
from pettingzoo.atari import entombed_competitive_v3
from pettingzoo.atari import entombed_cooperative_v3
from pettingzoo.atari import flag_capture_v2
from pettingzoo.atari import foozpong_v3
from pettingzoo.atari import ice_hockey_v2
from pettingzoo.atari import joust_v3
from pettingzoo.atari import mario_bros_v3
from pettingzoo.atari import maze_craze_v3
from pettingzoo.atari import othello_v3
from pettingzoo.atari import pong_v3
from pettingzoo.atari import quadrapong_v4
from pettingzoo.atari import space_invaders_v2
from pettingzoo.atari import space_war_v2
from pettingzoo.atari import surround_v2
from pettingzoo.atari import tennis_v3
from pettingzoo.atari import video_checkers_v4
from pettingzoo.atari import volleyball_pong_v3
from pettingzoo.atari import wizard_of_wor_v3
from pettingzoo.atari import warlords_v3

from pettingzoo.classic import chess_v5
from pettingzoo.classic import checkers_v3
from pettingzoo.classic import rps_v2
from pettingzoo.classic import connect_four_v3
from pettingzoo.classic import tictactoe_v3
from pettingzoo.classic import leduc_holdem_v4
from pettingzoo.classic import mahjong_v4
from pettingzoo.classic import texas_holdem_v4
from pettingzoo.classic import texas_holdem_no_limit_v6
from pettingzoo.classic import uno_v4
from pettingzoo.classic import dou_dizhu_v4
from pettingzoo.classic import gin_rummy_v4
from pettingzoo.classic import go_v5
from pettingzoo.classic import hanabi_v4
from pettingzoo.classic import backgammon_v3

from pettingzoo.butterfly import knights_archers_zombies_v10
from pettingzoo.butterfly import pistonball_v6
from pettingzoo.butterfly import cooperative_pong_v5
from pettingzoo.butterfly import prospector_v4

from pettingzoo.magent import battle_v4
from pettingzoo.magent import adversarial_pursuit_v4
from pettingzoo.magent import gather_v5
from pettingzoo.magent import combined_arms_v6
from pettingzoo.magent import tiger_deer_v4
from pettingzoo.magent import battlefield_v5

from pettingzoo.mpe import simple_adversary_v2
from pettingzoo.mpe import simple_crypto_v2
from pettingzoo.mpe import simple_push_v2
from pettingzoo.mpe import simple_reference_v2
from pettingzoo.mpe import simple_speaker_listener_v3
from pettingzoo.mpe import simple_spread_v2
from pettingzoo.mpe import simple_tag_v2
from pettingzoo.mpe import simple_world_comm_v2
from pettingzoo.mpe import simple_v2

from pettingzoo.sisl import pursuit_v4
from pettingzoo.sisl import waterworld_v3
from pettingzoo.sisl import multiwalker_v9

all_prefixes = ["atari", "classic", "butterfly", "magent", "mpe", "sisl"]

manual_environments = {
    "butterfly/knights_archers_zombies",
    "butterfly/pistonball",
    "butterfly/cooperative_pong",
    "butterfly/prospector",
    "sisl/pursuit"
}

all_environments = {
    "atari/basketball_pong_v3": basketball_pong_v3,
    "atari/boxing_v2": boxing_v2,
    "atari/combat_tank_v2": combat_tank_v2,
    "atari/combat_plane_v2": combat_plane_v2,
    "atari/double_dunk_v3": double_dunk_v3,
    "atari/entombed_cooperative_v3": entombed_cooperative_v3,
    "atari/entombed_competitive_v3": entombed_competitive_v3,
    "atari/flag_capture_v2": flag_capture_v2,
    "atari/foozpong_v3": foozpong_v3,
    "atari/joust_v3": joust_v3,
    "atari/ice_hockey_v2": ice_hockey_v2,
    "atari/maze_craze_v3": maze_craze_v3,
    "atari/mario_bros_v3": mario_bros_v3,
    "atari/othello_v3": othello_v3,
    "atari/pong_v3": pong_v3,
    "atari/quadrapong_v4": quadrapong_v4,
    "atari/space_invaders_v2": space_invaders_v2,
    "atari/space_war_v2": space_war_v2,
    "atari/surround_v2": surround_v2,
    "atari/tennis_v3": tennis_v3,
    "atari/video_checkers_v4": video_checkers_v4,
    "atari/volleyball_pong_v3": volleyball_pong_v3,
    "atari/wizard_of_wor_v3": wizard_of_wor_v3,
    "atari/warlords_v3": warlords_v3,

    "classic/chess_v5": chess_v5,
    "classic/checkers_v3": checkers_v3,
    "classic/rps_v2": rps_v2,
    "classic/connect_four_v3": connect_four_v3,
    "classic/tictactoe_v3": tictactoe_v3,
    "classic/leduc_holdem_v4": leduc_holdem_v4,
    "classic/mahjong_v4": mahjong_v4,
    "classic/texas_holdem_v4": texas_holdem_v4,
    "classic/texas_holdem_no_limit_v6": texas_holdem_no_limit_v6,
    "classic/uno_v4": uno_v4,
    "classic/dou_dizhu_v4": dou_dizhu_v4,
    "classic/gin_rummy_v4": gin_rummy_v4,
    "classic/go_v5": go_v5,
    "classic/hanabi_v4": hanabi_v4,
    "classic/backgammon_v3": backgammon_v3,

    "butterfly/knights_archers_zombies_v10": knights_archers_zombies_v10,
    "butterfly/pistonball_v6": pistonball_v6,
    "butterfly/cooperative_pong_v5": cooperative_pong_v5,
    "butterfly/prospector_v4": prospector_v4,

    "magent/adversarial_pursuit_v4": adversarial_pursuit_v4,
    "magent/battle_v4": battle_v4,
    "magent/battlefield_v5": battlefield_v5,
    "magent/combined_arms_v6": combined_arms_v6,
    "magent/gather_v5": gather_v5,
    "magent/tiger_deer_v4": tiger_deer_v4,

    "mpe/simple_adversary_v2": simple_adversary_v2,
    "mpe/simple_crypto_v2": simple_crypto_v2,
    "mpe/simple_push_v2": simple_push_v2,
    "mpe/simple_reference_v2": simple_reference_v2,
    "mpe/simple_speaker_listener_v3": simple_speaker_listener_v3,
    "mpe/simple_spread_v2": simple_spread_v2,
    "mpe/simple_tag_v2": simple_tag_v2,
    "mpe/simple_world_comm_v2": simple_world_comm_v2,
    "mpe/simple_v2": simple_v2,

    "sisl/multiwalker_v9": multiwalker_v9,
    "sisl/waterworld_v3": waterworld_v3,
    "sisl/pursuit_v4": pursuit_v4,
}
