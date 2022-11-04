# noqa
"""
# Maze Craze

```{figure} atari_maze_craze.gif
:width: 140px
:name: maze_craze
```

This environment is part of the <a href='..'>Atari environments</a>. Please read that page first for general information.

| Import               | `from pettingzoo.atari import maze_craze_v3` |
|----------------------|----------------------------------------------|
| Actions              | Discrete                                     |
| Parallel API         | Yes                                          |
| Manual Control       | No                                           |
| Agents               | `agents= ['first_0', 'second_0']`            |
| Agents               | 2                                            |
| Action Shape         | (1,)                                         |
| Action Values        | [0,17]                                       |
| Observation Shape    | (250, 160, 3)                                |
| Observation Values   | (0,255)                                      |


A competitive game of memory and planning!

Its a race to leave the maze. There are 3 main versions of the game.

1. **Race**: A basic version of the game. First to leave the maze wins
2. **Robbers**: There are 2 robbers randomly traversing the maze. If you are captured by the robbers, you lose the game, and receive -1 reward, and will be done. The player that has not been captured will not receive any reward, but they can still exit the maze and win, scoring +1 reward.
3. **Capture**: Each player have to capture all 3 robbers before you are able to exit the maze. Additionally, you can confuse your opponent (and yourself, if you are not careful!) by creating a block that looks identical to a wall in the maze, but all players can pass through it. You can only
create one wall at a time, when you create a new one, the old one disappears.

The first player to leave the maze scores +1, the other player scores -1 (unless that other player has already been captured in Robbers mode).

[Official Maze craze manual](https://atariage.com/manual_html_page.php?SoftwareLabelID=295). Note that the table of modes has some inaccuracies. In particular, game mode 12 has Blockade enabled, not mode 11.

#### Environment parameters

Some environment parameters are common to all Atari environments and are described in the [base Atari documentation](../atari).

Parameters specific to Maze Craze are

``` python
maze_craze.env(game_version="robbers", visibilty_level=0)
```

`game_version`:  Possibilities are "robbers", "race", "capture", corresponding to the 3 game versions described above

`visibilty_level`:  A number from 0-3. Set to 0 for 100% visible map, and 3 for 0% visibility map.

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
import warnings
from glob import glob

from ..base_atari_env import BaseAtariEnv, base_env_wrapper_fn, parallel_wrapper_fn

avaliable_versions = {
    "robbers": 2,
    "race": 1,
    "capture": 12,
}


def raw_env(game_version="robbers", visibilty_level=0, **kwargs):
    if game_version == "robbers" and visibilty_level == 0:
        warnings.warn(
            "maze_craze has different versions of the game via the `game_version` argument, consider overriding."
        )
    assert (
        game_version in avaliable_versions
    ), f"`game_version` parameter must be one of {avaliable_versions.keys()}"
    assert (
        0 <= visibilty_level < 4
    ), "visibility level must be between 0 and 4, where 0 is 100% visibility and 3 is 0% visibility"
    base_mode = (avaliable_versions[game_version] - 1) * 4
    mode = base_mode + visibilty_level
    name = os.path.basename(__file__).split(".")[0]
    parent_file = glob(
        os.path.join(os.path.dirname(os.path.dirname(__file__)), name + "*.py")
    )
    version_num = parent_file[0].split("_")[-1].split(".")[0]
    name = name + "_" + version_num
    return BaseAtariEnv(
        game="maze_craze",
        num_players=2,
        mode_num=mode,
        env_name=name,
        **kwargs,
    )


env = base_env_wrapper_fn(raw_env)
parallel_env = parallel_wrapper_fn(env)
