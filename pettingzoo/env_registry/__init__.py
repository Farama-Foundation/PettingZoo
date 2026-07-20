"""
Built-in environment registration for PettingZoo.

Importing this module populates the AEC and parallel registries with all
built-in environments. This mimics Gymnasium's API design.
"""

import re
from pathlib import Path

from pettingzoo.env_registry.registration import register

# Internal helpers for checking whether an environment provides parallel API

_PACKAGE_ROOT = Path(__file__).parent.parent.resolve()
_SOURCE_CACHE: dict[str, str] = {}


def _module_source(module: str) -> str:
    """Return source text for ``module`` without importing it."""
    if module not in _SOURCE_CACHE:
        parts = module.split(".")
        path = _PACKAGE_ROOT.joinpath(*parts[1:]).with_suffix(".py")
        _SOURCE_CACHE[module] = path.read_text(encoding="utf-8")
    return _SOURCE_CACHE[module]


def _maybe_register_parallel(
    _id: str,
    _module: str,
    *,
    keyword: str = "parallel_env",
) -> None:
    """Register a parallel entry point only if it is defined in the source code."""
    src = _module_source(_module)
    if re.search(r"^" + keyword + " =", src, re.MULTILINE) or re.search(
        r"def " + keyword, src
    ):
        register("parallel", _id, entry_point=f"{_module}:{keyword}")


# Atari environments

_atari_envs = [
    ("basketball_pong_v3", "basketball_pong"),
    ("boxing_v2", "boxing"),
    ("combat_plane_v2", "combat_plane"),
    ("combat_tank_v2", "combat_tank"),
    ("double_dunk_v3", "double_dunk"),
    ("entombed_competitive_v3", "entombed_competitive"),
    ("entombed_cooperative_v3", "entombed_cooperative"),
    ("flag_capture_v2", "flag_capture"),
    ("foozpong_v3", "foozpong"),
    ("ice_hockey_v2", "ice_hockey"),
    ("joust_v3", "joust"),
    ("mario_bros_v3", "mario_bros"),
    ("maze_craze_v3", "maze_craze"),
    ("othello_v3", "othello"),
    ("pong_v3", "pong"),
    ("quadrapong_v4", "quadrapong"),
    ("space_invaders_v2", "space_invaders"),
    ("space_war_v2", "space_war"),
    ("surround_v2", "surround"),
    ("tennis_v3", "tennis"),
    ("video_checkers_v4", "video_checkers"),
    ("volleyball_pong_v3", "volleyball_pong"),
    ("warlords_v3", "warlords"),
    ("wizard_of_wor_v3", "wizard_of_wor"),
]

for _id, _base in _atari_envs:
    _module = f"pettingzoo.atari.{_base}.{_base}"
    register("aec", f"atari/{_id}", entry_point=f"{_module}:env")
    _maybe_register_parallel(f"atari/{_id}", _module)

# Butterfly environments

_butterfly_envs = [
    ("knights_archers_zombies_v11", "knights_archers_zombies"),
    ("pistonball_v6", "pistonball"),
    ("cooperative_pong_v6", "cooperative_pong"),
]

for _id, _base in _butterfly_envs:
    _module = f"pettingzoo.butterfly.{_base}.{_base}"
    register("aec", f"butterfly/{_id}", entry_point=f"{_module}:env")
    _maybe_register_parallel(f"butterfly/{_id}", _module)

# Classic environments

_classic_envs = [
    ("chess_v6", "pettingzoo.classic.chess.chess"),
    ("rps_v2", "pettingzoo.classic.rps.rps"),
    ("connect_four_v3", "pettingzoo.classic.connect_four.connect_four"),
    ("tictactoe_v3", "pettingzoo.classic.tictactoe.tictactoe"),
    ("leduc_holdem_v4", "pettingzoo.classic.rlcard_envs.leduc_holdem"),
    ("texas_holdem_v4", "pettingzoo.classic.rlcard_envs.texas_holdem"),
    (
        "texas_holdem_no_limit_v6",
        "pettingzoo.classic.rlcard_envs.texas_holdem_no_limit",
    ),
    ("go_v5", "pettingzoo.classic.go.go"),
    ("hanabi_v5", "pettingzoo.classic.hanabi.hanabi"),
]

for _id, _module in _classic_envs:
    register("aec", f"classic/{_id}", entry_point=f"{_module}:env")
    _maybe_register_parallel(f"classic/{_id}", _module)

# SISL environments

_sisl_envs = [
    ("multiwalker_v9", "multiwalker"),
    ("pursuit_v5", "pursuit"),
]

for _id, _base in _sisl_envs:
    _module = f"pettingzoo.sisl.{_base}.{_base}"
    register("aec", f"sisl/{_id}", entry_point=f"{_module}:env")
    _maybe_register_parallel(f"sisl/{_id}", _module)

_SOURCE_CACHE.clear()
