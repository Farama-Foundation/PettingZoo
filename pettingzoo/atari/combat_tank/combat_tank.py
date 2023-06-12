# noqa: D212, D415
"""
# Combat: Tank

```{figure} atari_combat_tank.gif
:width: 140px
:name: combat_tank
```

This environment is part of the <a href='..'>Atari environments</a>. Please read that page first for general information.

| Import             | `from pettingzoo.atari import combat_tank_v3`     |
|--------------------|---------------------------------------------------|
| Actions            | Discrete                                          |
| Parallel API       | Yes                                               |
| Manual Control     | No                                                |
| Agents             | `agents= ['first_0', 'second_0']`                 |
| Agents             | 2                                                 |
| Action Shape       | (1,)                                              |
| Action Values      | [0,5]                                             |
| Observation Shape  | (210, 160, 3)                                     |
| Observation Values | (0,255)                                           |


*Combat*'s classic tank mode is an adversarial game where prediction, and positioning are key.

The players move around the map. When your opponent is hit by your bullet,
you score a point. Note that your opponent gets blasted through obstacles when it is hit, potentially putting it in a good position to hit you back.

Whenever you score a point, you are rewarded +1 and your opponent is penalized -1.

[Official Combat manual](https://atariage.com/manual_html_page.php?SoftwareID=935)


#### Environment parameters

Some environment parameters are common to all Atari environments and are described in the [base Atari documentation](../atari).

Parameters specific to combat-tank are

``` python
combat_tank_v2.env(has_maze=True, is_invisible=False, billiard_hit=True)
```

`has_maze`:  Set to true to have the map be a maze instead of an open field

`is_invisible`:  If true, tanks are invisible unless they are firing or are running into a wall.

`billiard_hit`:  If true, bullets bounce off walls, in fact, like billiards, they only count if they hit the opponent's tank after bouncing off a wall.

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
import warnings
from glob import glob

from pettingzoo.atari.base_atari_env import (
    BaseAtariEnv,
    base_env_wrapper_fn,
    parallel_wrapper_fn,
)


def raw_env(has_maze=True, is_invisible=False, billiard_hit=True, **kwargs):
    if has_maze is False and is_invisible is False and billiard_hit is False:
        warnings.warn(
            "combat_tank has interesting parameters to consider overriding including is_invisible, billiard_hit and has_maze"
        )
    start_mapping = {
        (False, False): 1,
        (False, True): 8,
        (True, False): 10,
        (True, True): 13,
    }
    mode = start_mapping[(is_invisible, billiard_hit)] + has_maze
    name = os.path.basename(__file__).split(".")[0]
    parent_file = glob(
        os.path.join(os.path.dirname(os.path.dirname(__file__)), name + "*.py")
    )
    version_num = parent_file[0].split("_")[-1].split(".")[0]
    name = name + "_" + version_num
    return BaseAtariEnv(
        game="combat", num_players=2, mode_num=mode, env_name=name, **kwargs
    )


env = base_env_wrapper_fn(raw_env)
parallel_env = parallel_wrapper_fn(env)
