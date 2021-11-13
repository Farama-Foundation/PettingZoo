import os

from .base_atari_env import BaseAtariEnv, base_env_wrapper_fn, parallel_wrapper_fn

"""
A battle of memory and information.

A flag is hidden
on the map.
You can travel through the map and check
the squares in it. If it is the flag,
you score a point (and your opponent is penalized).
If it is a bomb, you get sent back to your starting location.
Otherwise, it will give you a hint to where the flag is,
either a direction or a distance.
Your player needs to be able to use information from both
your own search and your opponent's search in order to
narrow down the location of the flag quickly and effectively.

[Official flag capture manual](https://atariage.com/manual_html_page.php?SoftwareLabelID=183)


#### Environment parameters

Environment parameters are common to all Atari environments and are described in the [base Atari documentation](../atari) .
"""

def raw_env(**kwargs):
    return BaseAtariEnv(game="flag_capture", num_players=2, mode_num=None, env_name=os.path.basename(__file__)[:-3], **kwargs)


env = base_env_wrapper_fn(raw_env)
parallel_env = parallel_wrapper_fn(env)
