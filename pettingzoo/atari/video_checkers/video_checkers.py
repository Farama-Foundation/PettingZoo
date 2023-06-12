# noqa: D212, D415
"""
# Video Checkers

```{figure} atari_video_checkers.gif
:width: 140px
:name: video_checkers
```

This environment is part of the <a href='..'>Atari environments</a>. Please read that page first for general information.

| Import               | `from pettingzoo.atari import video_checkers_v4` |
|----------------------|--------------------------------------------------|
| Actions              | Discrete                                         |
| Parallel API         | Yes                                              |
| Manual Control       | No                                               |
| Agents               | `agents= ['first_0', 'second_0']`                |
| Agents               | 2                                                |
| Action Shape         | (1,)                                             |
| Action Values        | [0,4]                                            |
| Observation Shape    | (210, 160, 3)                                    |
| Observation Values   | (0,255)                                          |


A classical strategy game with arcade style controls.

Capture all of your opponents pieces by jumping over them. To move a piece, you must select a piece by hovering the cursor and pressing fire (action 1), moving the cursor, and pressing fire again. Note that the buttons must be held for multiple frames to be registered.

If you win by capturing all your opponent's pieces, you are rewarded +1 and your opponent -1.

This is a timed game: if a player does not take a turn after 10 seconds, then that player is rewarded -1 points, their opponent is rewarded nothing, and the timer resets. This prevents one player from indefinitely stalling the game, but also means it is no longer a purely zero sum game.


[Official video checkers manual](https://atariage.com/manual_html_page.php?SoftwareID=1427)

#### Environment parameters

Environment parameters are common to all Atari environments and are described in the [base Atari documentation](../atari) .

### Action Space (Minimal)

In any given turn, an agent can choose from one of 5 actions.

| Action    | Behavior  |
|:---------:|-----------|
| 0         | Fire |
| 1         | Move up |
| 2         | Move right |
| 3         | Move left |
| 4         | Move down |


### Version History

* v4: Minimal Action Space (1.18.0)
* v3: No action timer (1.9.0)
* v2: Fixed checkers rewards (1.5.0)
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
        game="video_checkers", num_players=2, mode_num=None, env_name=name, **kwargs
    )


env = base_env_wrapper_fn(raw_env)
parallel_env = parallel_wrapper_fn(env)
