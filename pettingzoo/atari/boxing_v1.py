import os

from .base_atari_env import BaseAtariEnv, base_env_wrapper_fn, parallel_wrapper_fn

"""
*Boxing* is an adversarial game where precise control and
appropriate responses to your opponent are key.

The players have two minutes (around 1200 steps) to duke it
out in the ring. Each step, they can move and punch.
Successful punches score points,
1 point for a long jab, 2 for a close power punch,
and 100 points for a KO (which also will end the game).
Whenever you score a number of points, you are rewarded by
that number and your opponent is penalized by that number.

[Official Boxing manual](https://atariage.com/manual_html_page.php?SoftwareLabelID=45)

#### Environment parameters

Environment parameters are common to all Atari environments and are described in the [base Atari documentation](../atari) .
"""

def raw_env(**kwargs):
    return BaseAtariEnv(game="boxing", num_players=2, mode_num=None, env_name=os.path.basename(__file__)[:-3], **kwargs)


env = base_env_wrapper_fn(raw_env)
parallel_env = parallel_wrapper_fn(env)
