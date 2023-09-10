# noqa: D212, D415
"""
# Flag Capture

```{figure} atari_flag_capture.gif
:width: 140px
:name: flag_capture
```

This environment is part of the <a href='..'>Atari environments</a>. Please read that page first for general information.

| Import               | `from pettingzoo.atari import flag_capture_v2` |
|----------------------|------------------------------------------------|
| Actions              | Discrete                                       |
| Parallel API         | Yes                                            |
| Manual Control       | No                                             |
| Agents               | `agents= ['first_0', 'second_0']`              |
| Agents               | 2                                              |
| Action Shape         | (1,)                                           |
| Action Values        | [0,9]                                          |
| Observation Shape    | (210, 160, 3)                                  |
| Observation Values   | (0,255)                                        |


A battle of memory and information.

A flag is hidden
on the map.
You can travel through the map and check
the squares in it. If it is the flag,
you score a point (and your opponent is penalized).
If it is a bomb, you get sent back to your starting location.
Otherwise, it will give you a hint to where the flag is,
either a direction or a distance.
Your player needs to be able to use information from both
your own search and your opponent's search in order to
narrow down the location of the flag quickly and effectively.

[Official flag capture manual](https://atariage.com/manual_html_page.php?SoftwareLabelID=183)


#### Environment parameters

Environment parameters are common to all Atari environments and are described in the [base Atari documentation](../atari) .

### Action Space (Minimal)

In any given turn, an agent can choose from one of 10 actions.

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


def raw_env(**kwargs):
    name = os.path.basename(__file__).split(".")[0]
    parent_file = glob(
        os.path.join(os.path.dirname(os.path.dirname(__file__)), name + "*.py")
    )
    version_num = parent_file[0].split("_")[-1].split(".")[0]
    name = name + "_" + version_num
    return BaseAtariEnv(
        game="flag_capture", num_players=2, mode_num=None, env_name=name, **kwargs
    )


env = base_env_wrapper_fn(raw_env)
parallel_env = parallel_wrapper_fn(env)
