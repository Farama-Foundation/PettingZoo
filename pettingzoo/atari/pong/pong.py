# noqa: D212, D415
"""
# Pong

```{figure} atari_pong.gif
:width: 140px
:name: pong
```

This environment is part of the <a href='..'>Atari environments</a>. Please read that page first for general information.

| Import               | `from pettingzoo.atari import pong_v3` |
|----------------------|----------------------------------------|
| Actions              | Discrete                               |
| Parallel API         | Yes                                    |
| Manual Control       | No                                     |
| Agents               | `agents= ['first_0', 'second_0']`      |
| Agents               | 2                                      |
| Action Shape         | (1,)                                   |
| Action Values        | [0,5]                                  |
| Observation Shape    | (210, 160, 3)                          |
| Observation Values   | (0,255)                                |


Classic two player competitive game of timing.

Get the ball past the opponent.

Scoring a point gives you +1 reward and your opponent -1 reward.

Serves are timed: If the player does not serve within 2 seconds of receiving the ball, they receive -1 points, and the timer resets. This prevents one player from indefinitely stalling the game, but also means it is no longer a purely zero sum game.

[Official Video Olympics manual](https://atariage.com/manual_html_page.php?SoftwareLabelID=587)

#### Environment parameters

Some environment parameters are common to all Atari environments and are described in the [base Atari documentation](../atari).

Parameters specific to Pong are

``` python
pong_v3.env(num_players=2)
```

`num_players`:  Number of players (must be either 2 or 4)

### Action Space (Minimal)

In any given turn, an agent can choose from one of 6 actions.

| Action    | Behavior  |
|:---------:|-----------|
| 0         | No operation |
| 1         | Fire |
| 2         | Move right |
| 3         | Move left |
| 4         | Fire right |
| 5         | Fire left |

### Version History

* v3: Minimal Action Space (1.18.0)
* v2: No action timer (1.9.0)
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

avaliable_2p_versions = {
    "classic": 4,
    "two_paddles": 10,
    "soccer": 14,
    "foozpong": 19,
    "hockey": 27,
    "handball": 35,
    "volleyball": 39,
    "basketball": 45,
}
avaliable_4p_versions = {
    "classic": 6,
    "two_paddles": 11,
    "soccer": 16,
    "foozpong": 21,
    "hockey": 29,
    "quadrapong": 33,
    "handball": 37,
    "volleyball": 41,
    "basketball": 49,
}


def raw_env(num_players=2, game_version="classic", **kwargs):
    assert num_players == 2 or num_players == 4, "pong only supports 2 or 4 players"
    versions = avaliable_2p_versions if num_players == 2 else avaliable_4p_versions
    assert (
        game_version in versions
    ), f"pong version {game_version} not supported for number of players {num_players}. Available options are {list(versions)}"
    mode = versions[game_version]
    name = os.path.basename(__file__).split(".")[0]
    parent_file = glob(
        os.path.join(os.path.dirname(os.path.dirname(__file__)), name + "*.py")
    )
    version_num = parent_file[0].split("_")[-1].split(".")[0]
    name = name + "_" + version_num
    return BaseAtariEnv(
        game="pong",
        num_players=num_players,
        mode_num=mode,
        env_name=name,
        **kwargs,
    )


env = base_env_wrapper_fn(raw_env)
parallel_env = parallel_wrapper_fn(env)
