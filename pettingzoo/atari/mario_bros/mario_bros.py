# noqa
"""
# Mario Bros

```{figure} atari_mario_bros.gif
:width: 140px
:name: mario_bros
```

This environment is part of the <a href='..'>Atari environments</a>. Please read that page first for general information.

| Import               | `from pettingzoo.atari import mario_bros_v3` |
|----------------------|----------------------------------------------|
| Actions              | Discrete                                     |
| Parallel API         | Yes                                          |
| Manual Control       | No                                           |
| Agents               | `agents= ['first_0', 'second_0']`            |
| Agents               | 2                                            |
| Action Shape         | (1,)                                         |
| Action Values        | [0,17]                                       |
| Observation Shape    | (210, 160, 3)                                |
| Observation Values   | (0,255)                                      |


A mixed-sum game of planning and control.

The main goal is to kick a pest off the floor. This requires 2 steps:

1. Hit the floor below the pest, flipping it over. This knocks the pest on its back.
2. You to move up onto the floor where the pest is and you can kick it off. This earns +800 reward

Note that since this process has two steps there are opportunities for the two agents to either collaborate by helping each other knock pests over and collect them (potentially allowing both to collect reward more quickly), or for agents to steal the other's work.

If you run into an active pest or a fireball, you lose a life. If you lose all your lives, you are done, and the other player keeps playing. You can gain a new life after earning 20000 points.

There are other ways of earning points, by collecting bonus coins or wafers, earning 800 points each.

[Official mario bros manual](https://atariage.com/manual_html_page.php?SoftwareLabelID=286)

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
* v2: Breaking changes to entire API (1.4.0)
* v1: Fixes to how all environments handle premature death (1.3.0)
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
        game="mario_bros", num_players=2, mode_num=None, env_name=name, **kwargs
    )


env = base_env_wrapper_fn(raw_env)
parallel_env = parallel_wrapper_fn(env)
