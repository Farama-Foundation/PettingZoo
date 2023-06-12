# noqa: D212, D415
"""
# Emtombed: Cooperative

```{figure} atari_entombed_cooperative.gif
:width: 140px
:name: entombed_cooperative
```

This environment is part of the <a href='..'>Atari environments</a>. Please read that page first for general information.

| Import               | `from pettingzoo.atari import entombed_cooperative_v3` |
|----------------------|--------------------------------------------------------|
| Actions              | Discrete                                               |
| Parallel API         | Yes                                                    |
| Manual Control       | No                                                     |
| Agents               | `agents= ['first_0', 'second_0']`                      |
| Agents               | 2                                                      |
| Action Shape         | (1,)                                                   |
| Action Values        | [0,17]                                                 |
| Observation Shape    | (210, 160, 3)                                          |
| Observation Values   | (0,255)                                                |
| Average Total Reward | 6.23                                                   |


Entombed's cooperative version is an exploration game
where you need to work with your teammate to make it
as far as possible into the maze.

You both need to quickly navigate down a constantly generating
maze you can only see part of. If you get stuck, you lose.
Note you can easily find yourself in a dead-end escapable only through the use of rare power-ups.
If players help each other by the use of these powerups, they can last longer. Note that optimal coordination requires that the agents be on opposite sides of the map, because powerups appear on one side or the other, but can be used to break through walls on both sides
(the break is symmetric and effects both halves of the screen).
In addition, there dangerous zombies lurking around to avoid.

The reward was designed to be identical to the single player rewards. In particular, an entombed stage is divided into 5 invisible sections. You receive reward immediately after changing sections, or after resetting the stage. Note that this means that you receive a reward when you lose a life,
because it resets the stage, but not when you lose your last life, because the game terminates without the stage resetting.


[Official Entombed manual](https://atariage.com/manual_html_page.php?SoftwareLabelID=165)


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
* v2: Breaking changes to entire API, fixed Entombed rewards (1.4.0)
* v1: Fixes to how all environments handle premature death (1.3.0)
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
        game="entombed", num_players=2, mode_num=3, env_name=name, **kwargs
    )


env = base_env_wrapper_fn(raw_env)
parallel_env = parallel_wrapper_fn(env)
