import os

from .base_atari_env import BaseAtariEnv, base_env_wrapper_fn, parallel_wrapper_fn

"""
Four player last man standing!

Defend your fortress from the ball and hit it towards your opponents.

When your fortress falls, you receive -1 reward and are done. If you are the last player standing, you receive +1 reward.

[Official wizard_of_wor manual](https://atariage.com/manual_html_page.php?SoftwareLabelID=598)

### Arguments

Environment parameters are common to all Atari environments and are described in the [base Atari documentation](../atari) .
"""

def raw_env(**kwargs):
    return BaseAtariEnv(game="warlords", num_players=4, mode_num=None, env_name=os.path.basename(__file__)[:-3], **kwargs)


env = base_env_wrapper_fn(raw_env)
parallel_env = parallel_wrapper_fn(env)
