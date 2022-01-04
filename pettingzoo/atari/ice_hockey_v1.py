import os

from .base_atari_env import BaseAtariEnv, base_env_wrapper_fn, parallel_wrapper_fn

"""
Competitive game of control and timing.

When you are on offense you must pass the puck between your two players (you control the one with the puck) to get it past your opponent's defense. On defense, you control the player directly in front of the puck. Both players must handle the rapid switches of control, while maneuvering around your opponent. If you score, you are rewarded +1, and your opponent -1.

[Official ice hockey manual](https://atariage.com/manual_html_page.php?SoftwareLabelID=241)


### Arguments

Environment parameters are common to all Atari environments and are described in the [base Atari documentation](../atari) .
"""

def raw_env(**kwargs):
    return BaseAtariEnv(game="ice_hockey", num_players=2, mode_num=None, env_name=os.path.basename(__file__)[:-3], **kwargs)


env = base_env_wrapper_fn(raw_env)
parallel_env = parallel_wrapper_fn(env)
