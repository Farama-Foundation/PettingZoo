import os

from .base_atari_env import BaseAtariEnv, base_env_wrapper_fn, parallel_wrapper_fn

"""
A competitive game of planning and strategy.

In surround, your goal is to avoid the walls. If you run into a wall, you are rewarded -1 points, and your opponent, +1 points.

But both players leave a trail of walls behind you, slowly filling the screen with obstacles. To avoid the obstacles as long as possible, you must plan your path to conserve space. Once that is mastered, a higher level aspect of the game comes into play, where both players literally try to surround the other with walls, so their opponent will run out of room and be forced to run into a wall.

[Official surround manual](https://atariage.com/manual_html_page.php?SoftwareLabelID=943)

### Arguments

Environment parameters are common to all Atari environments and are described in the [base Atari documentation](../atari) .
"""

def raw_env(**kwargs):
    return BaseAtariEnv(game="surround", num_players=2, mode_num=None, env_name=os.path.basename(__file__)[:-3], **kwargs)


env = base_env_wrapper_fn(raw_env)
parallel_env = parallel_wrapper_fn(env)
