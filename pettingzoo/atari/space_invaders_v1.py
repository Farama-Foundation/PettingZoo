import os

from .base_atari_env import BaseAtariEnv, base_env_wrapper_fn, parallel_wrapper_fn

"""
Classic Atari game, but there are two ships controlled by two players that are each trying to maximize their score.

This game has a cooperative aspect where the players can choose to maximize their score by working together to clear the levels. The normal aliens are 5-30 points, depending on how high up they start, and the ship that flies across the top of the screen is worth 100 points.

However, there is also a competitive aspect where a player receives a 200 point bonus when the other player is hit by the aliens. So sabotaging the other player somehow is a possible strategy.

The number of lives is shared between the ships, i.e. the game ends when a ship has been hit 3 times.

[Official Space Invaders manual](https://atariage.com/manual_html_page.php?SoftwareLabelID=460)

### Arguments

Some environment parameters are common to all Atari environments and are described in the [base Atari documentation](../atari).

Parameters specific to Space Invaders are

:param alternating_control:  Only one of the two players has an option to fire at one time. If you fire, your opponent can then fire. However, you can't hoard the firing ability forever, eventually, control shifts to your opponent anyways.
:param moving_shields:  The shields move back and forth, leaving less reliable protection.
:param zigzaging_bombs:  The invader's bombs move back and forth, making them more difficult to avoid.
:param fast_bomb:  The bombs are much faster, making them more difficult to avoid.
:param invisible_invaders:  The invaders are invisible, making them more difficult to hit.
"""

def raw_env(alternating_control=False, moving_shields=True, zigzaging_bombs=False, fast_bomb=False, invisible_invaders=False, **kwargs):
    mode = 33 + (
        moving_shields * 1
        + zigzaging_bombs * 2
        + fast_bomb * 4
        + invisible_invaders * 8
        + alternating_control * 16
    )
    return BaseAtariEnv(game="space_invaders", num_players=2, mode_num=mode, env_name=os.path.basename(__file__)[:-3], **kwargs)


env = base_env_wrapper_fn(raw_env)
parallel_env = parallel_wrapper_fn(env)
