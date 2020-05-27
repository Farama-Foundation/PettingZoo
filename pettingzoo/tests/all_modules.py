from pettingzoo.atari import *

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
from pettingzoo.classic import hanabi_v0
from pettingzoo.classic import backgammon_v0

from pettingzoo.gamma import knights_archers_zombies_v0
from pettingzoo.gamma import pistonball_v0
from pettingzoo.gamma import cooperative_pong_v0
from pettingzoo.gamma import prison_v0
from pettingzoo.gamma import prospector_v0

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
    "atari/boxing": boxing_v0,
    "atari/combat_tank": combat_tank_v0,
    "atari/combat_tankpong": combat_tankpong_v0,
    "atari/combat_invisible_tank": combat_invisible_tank_v0,
    "atari/combat_invisible_tankpong": combat_invisible_tankpong_v0,
    "atari/combat_biplane": combat_biplane_v0,
    "atari/combat_jet": combat_jet_v0,
    "atari/double_dunk": double_dunk_v0,
    "atari/entombed": entombed_v0,
    "atari/flag_capture": flag_capture_v0,
    "atari/joust": joust_v0,
    "atari/ice_hockey": ice_hockey_v0,
    "atari/maze_craze_fully_seen": maze_craze_fully_seen_v0,
    "atari/maze_craze_partial_vis": maze_craze_partial_vis_v0,
    "atari/maze_craze_invisible": maze_craze_invisible_v0,
    "atari/maze_craze_robbers": maze_craze_robbers_v0,
    "atari/maze_craze_capture": maze_craze_capture_v0,
    "atari/maze_craze_blockade": maze_craze_blockade_v0,
    "atari/mario_bros": mario_bros_v0,
    "atari/othello": othello_v0,
    "atari/pong": pong_v0,
    "atari/pong_basketball": pong_basketball_v0,
    "atari/space_invaders_easy": space_invaders_easy_v0,
    "atari/space_invaders_difficult": space_invaders_difficult_v0,
    "atari/space_invaders_alternating": space_invaders_alternating_v0,
    "atari/surround": surround_v0,
    "atari/surround_erase": surround_erase_v0,
    "atari/tennis": tennis_v0,
    "atari/video_checkers": video_checkers_v0,
    "atari/wizard_of_wor": wizard_of_wor_v0,
    "atari/warlords": warlords_v0,
    "atari/pong_four_player": pong_four_player_v0,
    "atari/pong_quadrapong": pong_quadrapong_v0,
    "atari/pong_volleyball": pong_volleyball_v0,

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
    "classic/hanabi": hanabi_v0,
    "classic/backgammon": backgammon_v0,

    "gamma/knights_archers_zombies": knights_archers_zombies_v0,
    "gamma/pistonball": pistonball_v0,
    "gamma/cooperative_pong": cooperative_pong_v0,
    "gamma/prison": prison_v0,
    "gamma/prospector": prospector_v0,

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
