import os

from .base_atari_env import BaseAtariEnv, base_env_wrapper_fn, parallel_wrapper_fn

"""
Battling both against NPCs and the other player. Careful timing,
and control is essential, as well as awareness of your opponent.

You score points by hitting the opponent and NPCs with your bullets. Hitting an NPC scores between 200 to 2500 points depending on the NCP, and hitting a player scores 1000 points.

If you get hit by a bullet, you lose a life. When both players lose 3 lives, the game is over.

Note that in addition to the competitive aspect where you benefit from attacking the other player, there is a cooperative aspect to the game where clearing levels means that both players will have more opportunities to score.

[Official Warlords manual](https://atariage.com/manual_html_page.php?SoftwareLabelID=593)

#### Environment parameters

Environment parameters are common to all Atari environments and are described in the [base Atari documentation](../atari) .
"""

def raw_env(**kwargs):
    return BaseAtariEnv(game="wizard_of_wor", num_players=2, mode_num=None, env_name=os.path.basename(__file__)[:-3], **kwargs)


env = base_env_wrapper_fn(raw_env)
parallel_env = parallel_wrapper_fn(env)
