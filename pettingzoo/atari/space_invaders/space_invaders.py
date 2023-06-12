# noqa: D212, D415
"""
# Space Invaders

```{figure} atari_space_invaders.gif
:width: 140px
:name: space_invaders
```

This environment is part of the <a href='..'>Atari environments</a>. Please read that page first for general information.

| Import               | `from pettingzoo.atari import space_invaders_v2` |
|----------------------|--------------------------------------------------|
| Actions              | Discrete                                         |
| Parallel API         | Yes                                              |
| Manual Control       | No                                               |
| Agents               | `agents= ['first_0', 'second_0']`                |
| Agents               | 2                                                |
| Action Shape         | (1,)                                             |
| Action Values        | [0,5]                                            |
| Observation Shape    | (210, 160, 3)                                    |
| Observation Values   | (0,255)                                          |


Classic Atari game, but there are two ships controlled by two players that are each trying to maximize their score.

This game has a cooperative aspect where the players can choose to maximize their score by working together to clear the levels. The normal aliens are 5-30 points, depending on how high up they start, and the ship that flies across the top of the screen is worth 100 points.

However, there is also a competitive aspect where a player receives a 200 point bonus when the other player is hit by the aliens. So sabotaging the other player somehow is a possible strategy.

The number of lives is shared between the ships, i.e. the game ends when a ship has been hit 3 times.

[Official Space Invaders manual](https://atariage.com/manual_html_page.php?SoftwareLabelID=460)

#### Environment parameters

Some environment parameters are common to all Atari environments and are described in the [base Atari documentation](../atari).

Parameters specific to Space Invaders are

``` python
space_invaders_v2.env(alternating_control=False, moving_shields=True,
zigzaging_bombs=False, fast_bomb=False, invisible_invaders=False)
```

`alternating_control`:  Only one of the two players has an option to fire at one time. If you fire, your opponent can then fire. However, you can't hoard the firing ability forever, eventually, control shifts to your opponent anyways.

`moving_shields`:  The shields move back and forth, leaving less reliable protection.

`zigzaging_bombs`:  The invader's bombs move back and forth, making them more difficult to avoid.

`fast_bomb`:  The bombs are much faster, making them more difficult to avoid.

`invisible_invaders`:  The invaders are invisible, making them more difficult to hit.

### Action Space (Minimal)

In any given turn, an agent can choose from one of 6 actions.

| Action    | Behavior  |
|:---------:|-----------|
| 0         | No operation |
| 1         | Fire |
| 2         | Move up |
| 3         | Move right |
| 4         | Move left |
| 5         | Move down |

### Version History

* v2: Minimal Action Space (1.18.0)
* v1: Breaking changes to entire API (1.4.0)
* v0: Initial versions release (1.0.0)


"""

import os
from glob import glob

from pettingzoo.atari.base_atari_env import (
    BaseAtariEnv,
    base_env_wrapper_fn,
    parallel_wrapper_fn,
)


def raw_env(
    alternating_control=False,
    moving_shields=True,
    zigzaging_bombs=False,
    fast_bomb=False,
    invisible_invaders=False,
    **kwargs,
):
    mode = 33 + (
        moving_shields * 1
        + zigzaging_bombs * 2
        + fast_bomb * 4
        + invisible_invaders * 8
        + alternating_control * 16
    )
    name = os.path.basename(__file__).split(".")[0]
    parent_file = glob(
        os.path.join(os.path.dirname(os.path.dirname(__file__)), name + "*.py")
    )
    version_num = parent_file[0].split("_")[-1].split(".")[0]
    name = name + "_" + version_num
    return BaseAtariEnv(
        game="space_invaders", num_players=2, mode_num=mode, env_name=name, **kwargs
    )


env = base_env_wrapper_fn(raw_env)
parallel_env = parallel_wrapper_fn(env)
