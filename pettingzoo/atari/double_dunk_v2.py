import os

from .base_atari_env import BaseAtariEnv, base_env_wrapper_fn, parallel_wrapper_fn

"""
An adversarial game that combines control and precise selection.

The game has two stages: selection and play. Selection can be
difficult because you have to hold the same action for a few steps and then
take the 0 action. Strategy choice is timed: if a player does not select any action after 2 seconds (120 frames)
then the player is rewarded -1, and the timer resets. This prevents one player from indefinitely stalling the game.

Once play begins, each team has two players. You only control
one at a time, and and which one you control depends on the selected play.
Scoring should be familiar to basketball fans (2-3 points per successful shot).

[Official double dunk manual](https://atariage.com/manual_html_page.php?SoftwareLabelID=153)


### Arguments

Environment parameters are common to all Atari environments and are described in the [base Atari documentation](../atari) .
"""

def raw_env(**kwargs):
    return BaseAtariEnv(game="double_dunk", num_players=2, mode_num=None, env_name=os.path.basename(__file__)[:-3], **kwargs)


env = base_env_wrapper_fn(raw_env)
parallel_env = parallel_wrapper_fn(env)
