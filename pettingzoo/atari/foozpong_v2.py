import os

from .base_atari_env import BaseAtariEnv, base_env_wrapper_fn, parallel_wrapper_fn

"""

Four player team battle.

Get the ball past your opponent's defenders to the scoring area. Like traditional foozball, the board has alternating layers of paddles from each team between the goal areas. To succeed at this game, the two players on each side must coordinate to allow the ball to be passed between these layers up the board and into your opponent's scoring area.

Scoring a point gives your team +1 reward and your opponent's team -1 reward.

Serves are timed: If the player does not serve within 2 seconds of receiving the ball, their team receives -1 points, and the timer resets. This prevents one player from indefinitely stalling the game, but also means it is no longer a purely zero sum game.


[Official Video Olympics manual](https://atariage.com/manual_html_page.php?SoftwareLabelID=587)

### Arguments

Some environment parameters are common to all Atari environments and are described in the [base Atari documentation](../atari).

Parameters specific to Foozpong are

:param num_players:  Number of players (must be either 2 or 4)
"""

def raw_env(num_players=4, **kwargs):
    assert num_players == 2 or num_players == 4, "pong only supports 2 or 4 players"
    mode_mapping = {2: 19, 4: 21}
    mode = mode_mapping[num_players]
    return BaseAtariEnv(game="pong", num_players=num_players, mode_num=mode, env_name=os.path.basename(__file__)[:-3], **kwargs)


env = base_env_wrapper_fn(raw_env)
parallel_env = parallel_wrapper_fn(env)
