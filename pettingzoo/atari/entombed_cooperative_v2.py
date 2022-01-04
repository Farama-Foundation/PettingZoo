import os

from .base_atari_env import BaseAtariEnv, base_env_wrapper_fn, parallel_wrapper_fn

"""
Entombed's cooperative version is an exploration game
where you need to work with your teammate to make it
as far as possible into the maze.

You both need to quickly navigate down a constantly generating
maze you can only see part of. If you get stuck, you lose.
Note you can easily find yourself in a dead-end escapable only through the use of rare power-ups.
If players help each other by the use of these powerups, they can last longer. Note that optimal coordination requires that the agents be on opposite sides of the map, because powerups appear on one side or the other, but can be used to break through walls on both sides (the break is symmetric and effects both halves of the screen).
In addition, there dangerous zombies lurking around to avoid.

The reward was designed to be identical to the single player rewards. In particular, an entombed stage is divided into 5 invisible sections. You receive reward immediately after changing sections, or after resetting the stage. Note that this means that you receive a reward when you lose a life, because it resets the stage, but not when you lose your last life, because the game terminates without the stage resetting.


[Official Entombed manual](https://atariage.com/manual_html_page.php?SoftwareLabelID=165)


### Arguments

Environment parameters are common to all Atari environments and are described in the [base Atari documentation](../atari) .
"""

def raw_env(**kwargs):
    return BaseAtariEnv(game="entombed", num_players=2, mode_num=3, env_name=os.path.basename(__file__)[:-3], **kwargs)


env = base_env_wrapper_fn(raw_env)
parallel_env = parallel_wrapper_fn(env)
