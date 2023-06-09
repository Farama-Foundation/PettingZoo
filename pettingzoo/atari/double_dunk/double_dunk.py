# noqa: D212, D415
"""
# Double Dunk

```{figure} atari_double_dunk.gif
:width: 140px
:name: double_dunk
```

This environment is part of the <a href='..'>Atari environments</a>. Please read that page first for general information.

| Import             | `from pettingzoo.atari import double_dunk_v3` |
|--------------------|-----------------------------------------------|
| Actions            | Discrete                                      |
| Parallel API       | Yes                                           |
| Manual Control     | No                                            |
| Agents             | agents= ['first_0', 'second_0']               |
| Agents             | 2                                             |
| Action Shape       | (1,)                                          |
| Action Values      | [0,17]                                        |
| Observation Shape  | (210, 160, 3)                                 |
| Observation Values | (0,255)                                       |


An adversarial game that combines control and precise selection.

The game has two stages: selection and play. Selection can be
difficult because you have to hold the same action for a few steps and then
take the 0 action. Strategy choice is timed: if a player does not select any action after 2 seconds (120 frames)
then the player is rewarded -1, and the timer resets. This prevents one player from indefinitely stalling the game, but also means it is no longer a purely zero sum game.

Once play begins, each team has two players. You only control
one at a time, and and which one you control depends on the selected play.
Scoring should be familiar to basketball fans (2-3 points per successful shot).

[Official double dunk manual](https://atariage.com/manual_html_page.php?SoftwareLabelID=153)


#### Environment parameters

Environment parameters are common to all Atari environments and are described in the [base Atari documentation](../atari) .

### Action Space

In any given turn, an agent can choose from one of 18 actions.

| Action    | Behavior  |
|:---------:|-----------|
| 0         | No operation |
| 1         | Fire |
| 2         | Move up |
| 3         | Move right |
| 4         | Move left |
| 5         | Move down |
| 6         | Move upright |
| 7         | Move upleft |
| 8         | Move downright |
| 9         | Move downleft |
| 10        | Fire up |
| 11        | Fire right |
| 12        | Fire left |
| 13        | Fire down |
| 14        | Fire upright |
| 15        | Fire upleft |
| 16        | Fire downright |
| 17        | Fire downleft |

### Version History

* v3: Minimal Action Space (1.18.0)
* v2: No action timer (1.9.0)
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


def raw_env(**kwargs):
    name = os.path.basename(__file__).split(".")[0]
    parent_file = glob(
        os.path.join(os.path.dirname(os.path.dirname(__file__)), name + "*.py")
    )
    version_num = parent_file[0].split("_")[-1].split(".")[0]
    name = name + "_" + version_num
    return BaseAtariEnv(
        game="double_dunk", num_players=2, mode_num=None, env_name=name, **kwargs
    )


env = base_env_wrapper_fn(raw_env)
parallel_env = parallel_wrapper_fn(env)
