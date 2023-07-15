# noqa: D212, D415
"""
# Space War

```{figure} atari_space_war.gif
:width: 140px
:name: space_war
```

This environment is part of the <a href='..'>Atari environments</a>. Please read that page first for general information.

| Import               | `from pettingzoo.atari import space_war_v2` |
|----------------------|---------------------------------------------|
| Actions              | Discrete                                    |
| Parallel API         | Yes                                         |
| Manual Control       | No                                          |
| Agents               | `agents= ['first_0', 'second_0']`           |
| Agents               | 2                                           |
| Action Shape         | (1,)                                        |
| Action Values        | [0,17]                                      |
| Observation Shape    | (250, 160, 3)                               |
| Observation Values   | (0,255)                                     |


*Space war* is an competitive game where prediction and positioning are key.

The players move around the map. When your opponent is hit by your bullet,
you score a point. The game is similar to combat, but with a more advanced physics system where acceleration and momentum need to be taken into account.

Whenever you score a point, you are rewarded +1 and your opponent is penalized -1.

[Official space war manual](https://atariage.com/manual_html_page.php?SoftwareLabelID=470)

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
        game="space_war", num_players=2, mode_num=None, env_name=name, **kwargs
    )


env = base_env_wrapper_fn(raw_env)
parallel_env = parallel_wrapper_fn(env)
