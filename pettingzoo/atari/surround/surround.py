# noqa
"""
# Surround

```{figure} atari_surround.gif
:width: 140px
:name: surround
```

This environment is part of the <a href='..'>Atari environments</a>. Please read that page first for general information.

| Import               | `from pettingzoo.atari import surround_v2` |
|----------------------|--------------------------------------------|
| Actions              | Discrete                                   |
| Parallel API         | Yes                                        |
| Manual Control       | No                                         |
| Agents               | `agents= ['first_0', 'second_0']`          |
| Agents               | 2                                          |
| Action Shape         | (1,)                                       |
| Action Values        | [0,4]                                      |
| Observation Shape    | (210, 160, 3)                              |
| Observation Values   | (0,255)                                    |


A competitive game of planning and strategy.

In surround, your goal is to avoid the walls. If you run into a wall, you are rewarded -1 points, and your opponent, +1 points.

But both players leave a trail of walls behind you, slowly filling the screen with obstacles. To avoid the obstacles as long as possible, you must plan your path to conserve space. Once that is mastered, a higher level aspect of the game comes into play, where both players literally try to
surround the other with walls, so their opponent will run out of room and be forced to run into a wall.

[Official surround manual](https://atariage.com/manual_html_page.php?SoftwareLabelID=943)

#### Environment parameters

Environment parameters are common to all Atari environments and are described in the [base Atari documentation](../atari) .

### Action Space (Minimal)

In any given turn, an agent can choose from one of 6 actions. (Fire is dummy action, but for the continuous numbering)

| Action    | Behavior  |
|:---------:|-----------|
| 0         | No operation |
| 1         | Fire (dummy) |
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

from ..base_atari_env import BaseAtariEnv, base_env_wrapper_fn, parallel_wrapper_fn


def raw_env(**kwargs):
    name = os.path.basename(__file__).split(".")[0]
    parent_file = glob(
        os.path.join(os.path.dirname(os.path.dirname(__file__)), name + "*.py")
    )
    version_num = parent_file[0].split("_")[-1].split(".")[0]
    name = name + "_" + version_num
    return BaseAtariEnv(
        game="surround", num_players=2, mode_num=None, env_name=name, **kwargs
    )


env = base_env_wrapper_fn(raw_env)
parallel_env = parallel_wrapper_fn(env)
