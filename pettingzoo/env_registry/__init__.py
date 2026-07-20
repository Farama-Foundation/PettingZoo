"""
Built-in environment registration for PettingZoo.

Importing this module populates the AEC and parallel registries with all
built-in environments. This mimics Gymnasium's API design.
"""

from pettingzoo.env_registry.registration import register

# Atari environments

_atari_envs = [
    "basketball_pong_v3",
    "boxing_v2",
    "combat_plane_v2",
    "combat_tank_v2",
    "double_dunk_v3",
    "entombed_competitive_v3",
    "entombed_cooperative_v3",
    "flag_capture_v2",
    "foozpong_v3",
    "ice_hockey_v2",
    "joust_v3",
    "mario_bros_v3",
    "maze_craze_v3",
    "othello_v3",
    "pong_v3",
    "quadrapong_v4",
    "space_invaders_v2",
    "space_war_v2",
    "surround_v2",
    "tennis_v3",
    "video_checkers_v4",
    "volleyball_pong_v3",
    "warlords_v3",
    "wizard_of_wor_v3",
]

for _name in _atari_envs:
    _base = _name.rsplit("_v", 1)[0]
    register(
        "aec", f"atari/{_name}", entry_point=f"pettingzoo.atari.{_base}.{_base}:env"
    )
    register(
        "parallel",
        f"atari/{_name}",
        entry_point=f"pettingzoo.atari.{_base}.{_base}:parallel_env",
    )

# Butterfly environments

_butterfly_envs = [
    ("knights_archers_zombies_v11", "knights_archers_zombies"),
    ("pistonball_v6", "pistonball"),
    ("cooperative_pong_v6", "cooperative_pong"),
]

for _id, _base in _butterfly_envs:
    register(
        "aec",
        f"butterfly/{_id}",
        entry_point=f"pettingzoo.butterfly.{_base}.{_base}:env",
    )
    register(
        "parallel",
        f"butterfly/{_id}",
        entry_point=f"pettingzoo.butterfly.{_base}.{_base}:parallel_env",
    )

# Classic environments

_classic_envs = [
    ("chess_v6", "chess"),
    ("rps_v2", "rps"),
    ("connect_four_v3", "connect_four"),
    ("tictactoe_v3", "tictactoe"),
    ("leduc_holdem_v4", "leduc_holdem"),
    ("texas_holdem_v4", "texas_holdem"),
    ("texas_holdem_no_limit_v6", "texas_holdem_no_limit"),
    ("go_v5", "go"),
    ("hanabi_v5", "hanabi"),
]

for _id, _base in _classic_envs:
    register(
        "aec", f"classic/{_id}", entry_point=f"pettingzoo.classic.{_base}.{_base}:env"
    )
    register(
        "parallel",
        f"classic/{_id}",
        entry_point=f"pettingzoo.classic.{_base}.{_base}:parallel_env",
    )

# SISL environments

_sisl_envs = [
    ("multiwalker_v9", "multiwalker"),
    ("pursuit_v6", "pursuit"),
]

for _id, _base in _sisl_envs:
    register("aec", f"sisl/{_id}", entry_point=f"pettingzoo.sisl.{_base}.{_base}:env")
    register(
        "parallel",
        f"sisl/{_id}",
        entry_point=f"pettingzoo.sisl.{_base}.{_base}:parallel_env",
    )
