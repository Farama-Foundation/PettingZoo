import os

from .base_atari_env import BaseAtariEnv, base_env_wrapper_fn, parallel_wrapper_fn

"""
*Combat*'s plane mode is an adversarial game where timing,
positioning, and keeping track of your opponent's complex
movements are key.

The players fly around the map, able to control flight direction
but not your speed.

When your opponent is hit by your bullet,
you score a point.

Whenever you score a point, you are rewarded +1 and your opponent is penalized -1.

[Official Combat manual](https://atariage.com/manual_html_page.php?SoftwareID=935)


### Arguments

Some environment parameters are common to all Atari environments and are described in the [base Atari documentation](../atari).

Parameters specific to combat-plane are

:param game_version:  Accepted arguments are "jet" or "bi-plane". Whether the plane is a bi-plane or a jet. (Jets move faster)
:param guided_missile:  Whether the missile can be directed after being fired, or whether it is on a fixed path.
"""

avaliable_versions = {
    "bi-plane": 15,
    "jet": 21,
}


def raw_env(game_version="bi-plane", guided_missile=True, **kwargs):
    assert game_version in avaliable_versions, "game_version must be either 'jet' or 'bi-plane'"
    mode = avaliable_versions[game_version] + (0 if guided_missile else 1)

    return BaseAtariEnv(game="combat", num_players=2, mode_num=mode, env_name=os.path.basename(__file__)[:-3], **kwargs)


env = base_env_wrapper_fn(raw_env)
parallel_env = parallel_wrapper_fn(env)
