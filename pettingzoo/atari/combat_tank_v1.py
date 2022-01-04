import os
import warnings

from .base_atari_env import BaseAtariEnv, base_env_wrapper_fn, parallel_wrapper_fn

"""
*Combat*'s classic tank mode is an adversarial game where prediction, and positioning are key.

The players move around the map. When your opponent is hit by your bullet,
you score a point. Note that your opponent gets blasted through obstacles when it is hit, potentially putting it in a good position to hit you back.

Whenever you score a point, you are rewarded +1 and your opponent is penalized -1.

[Official Combat manual](https://atariage.com/manual_html_page.php?SoftwareID=935)


### Arguments

Some environment parameters are common to all Atari environments and are described in the [base Atari documentation](../atari).

Parameters specific to combat-tank are

:param has_maze:  Set to true to have the map be a maze instead of an open field
:param is_invisible:  If true, tanks are invisible unless they are firing or are running into a wall.
:param billiard_hit:  If true, bullets bounce off walls, in fact, like billiards, they only count if they hit the opponent's tank after bouncing off a wall.
"""

def raw_env(has_maze=True, is_invisible=False, billiard_hit=True, **kwargs):
    if has_maze is False and is_invisible is False and billiard_hit is False:
        warnings.warn("combat_tank has interesting parameters to consider overriding including is_invisible, billiard_hit and has_maze")
    start_mapping = {
        (False, False): 1,
        (False, True): 8,
        (True, False): 10,
        (True, True): 13,
    }
    mode = start_mapping[(is_invisible, billiard_hit)] + has_maze

    return BaseAtariEnv(game="combat", num_players=2, mode_num=mode, env_name=os.path.basename(__file__)[:-3], **kwargs)


env = base_env_wrapper_fn(raw_env)
parallel_env = parallel_wrapper_fn(env)
