# noqa: D212, D415
"""
# Wizard of Wor

```{figure} atari_wizard_of_wor.gif
:width: 140px
:name: wizard_of_wor
```

This environment is part of the <a href='..'>Atari environments</a>. Please read that page first for general information.

| Import               | from pettingzoo.atari import wizard_of_wor_v3 |
|----------------------|-----------------------------------------------|
| Actions              | Discrete                                      |
| Parallel API         | Yes                                           |
| Manual Control       | No                                            |
| Agents               | agents= ['first_0', 'second_0']               |
| Agents               | 2                                             |
| Action Shape         | (1,)                                          |
| Action Values        | [0,8]                                         |
| Observation Shape    | (210, 160, 3)                                 |
| Observation Values   | (0,255)                                       |


Battling both against NPCs and the other player. Careful timing,
and control is essential, as well as awareness of your opponent.

You score points by hitting the opponent and NPCs with your bullets. Hitting an NPC scores between 200 to 2500 points depending on the NCP, and hitting a player scores 1000 points.

If you get hit by a bullet, you lose a life. When both players lose 3 lives, the game is over.

Note that in addition to the competitive aspect where you benefit from attacking the other player, there is a cooperative aspect to the game where clearing levels means that both players will have more opportunities to score.

[Official Warlords manual](https://atariage.com/manual_html_page.php?SoftwareLabelID=593)

#### Environment parameters

Environment parameters are common to all Atari environments and are described in the [base Atari documentation](../atari) .

### Action Space

In any given turn, an agent can choose from one of 9 actions.

| Action    | Behavior  |
|:---------:|-----------|
| 0         | Fire |
| 1         | Move up |
| 2         | Move right |
| 3         | Move left |
| 4         | Move down |
| 5         | Move upright |
| 6         | Move upleft |
| 7         | Move downright |
| 8         | Move downleft |

### Version History

* v3: Minimal Action Space (1.18.0)
* v2: Breaking changes to entire API (1.4.0)
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
        game="wizard_of_wor", num_players=2, mode_num=None, env_name=name, **kwargs
    )


env = base_env_wrapper_fn(raw_env)
parallel_env = parallel_wrapper_fn(env)
