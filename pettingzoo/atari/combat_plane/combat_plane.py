# noqa: D212, D415
"""
# Combat: Plane

```{figure} atari_combat_plane.gif
:width: 140px
:name: combat_plane
```

This environment is part of the <a href='..'>Atari environments</a>. Please read that page first for general information.

| Import             | `from pettingzoo.atari import combat_jet_v1` |
|--------------------|----------------------------------------------|
| Actions            | Discrete                                     |
| Parallel API       | Yes                                          |
| Manual Control     | No                                           |
| Agents             | `agents= ['first_0', 'second_0']`            |
| Agents             | 2                                            |
| Action Shape       | (1,)                                         |
| Action Values      | [0,17]                                       |
| Observation Shape  | (256, 160, 3)                                |
| Observation Values | (0,255)                                      |


*Combat*'s plane mode is an adversarial game where timing,
positioning, and keeping track of your opponent's complex
movements are key.

The players fly around the map, able to control flight direction
but not your speed.

When your opponent is hit by your bullet,
you score a point.

Whenever you score a point, you are rewarded +1 and your opponent is penalized -1.

[Official Combat manual](https://atariage.com/manual_html_page.php?SoftwareID=935)


#### Environment parameters

Some environment parameters are common to all Atari environments and are described in the [base Atari documentation](../atari).

Parameters specific to combat-plane are

``` python
combat_plane_v2.env(game_version="jet", guided_missile=True)
```

`game_version`:  Accepted arguments are "jet" or "bi-plane". Whether the plane is a bi-plane or a jet. (Jets move faster)

`guided_missile`:  Whether the missile can be directed after being fired, or whether it is on a fixed path.

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

avaliable_versions = {
    "bi-plane": 15,
    "jet": 21,
}


def raw_env(game_version="bi-plane", guided_missile=True, **kwargs):
    assert (
        game_version in avaliable_versions
    ), "game_version must be either 'jet' or 'bi-plane'"
    mode = avaliable_versions[game_version] + (0 if guided_missile else 1)
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
