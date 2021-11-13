import os

from .base_atari_env import BaseAtariEnv, base_env_wrapper_fn, parallel_wrapper_fn

"""
A mixed-sum game of planning and control.

The main goal is to kick a pest off the floor. This requires 2 steps:

1. Hit the floor below the pest, flipping it over. This knocks the pest on its back.
2. You to move up onto the floor where the pest is and you can kick it off. This earns +800 reward

Note that since this process has two steps there are opportunities for the two agents to either collaborate by helping each other knock pests over and collect them (potentially allowing both to collect reward more quickly), or for agents to steal the other's work.

If you run into an active pest or a fireball, you lose a life. If you lose all your lives, you are done, and the other player keeps playing. You can gain a new life after earning 20000 points.

There are other ways of earning points, by collecting bonus coins or wafers, earning 800 points each.

[Official mario bros manual](https://atariage.com/manual_html_page.php?SoftwareLabelID=286)

#### Environment parameters

Environment parameters are common to all Atari environments and are described in the [base Atari documentation](../atari) .
"""

def raw_env(**kwargs):
    return BaseAtariEnv(game="mario_bros", num_players=2, mode_num=None, env_name=os.path.basename(__file__)[:-3], **kwargs)


env = base_env_wrapper_fn(raw_env)
parallel_env = parallel_wrapper_fn(env)
