# noqa
"""
# Othello

```{figure} atari_othello.gif
:width: 140px
:name: othello
```

This environment is part of the <a href='..'>Atari environments</a>. Please read that page first for general information.

| Import               | `from pettingzoo.atari import othello_v3` |
|----------------------|-------------------------------------------|
| Actions              | Discrete                                  |
| Parallel API         | Yes                                       |
| Manual Control       | No                                        |
| Agents               | `agents= ['first_0', 'second_0']`         |
| Agents               | 2                                         |
| Action Shape         | (1,)                                      |
| Action Values        | [0,9]                                     |
| Observation Shape    | (210, 160, 3)                             |
| Observation Values   | (0,255)                                   |


The classic board game of long term strategy.

The goal is to flip over your opponents pieces. You can flip over your opponent's pieces (changing them to your color) by placing a piece in a row or diagonal which traps your opponents pieces between your own. You must capture at least one piece each turn
([othello rules](https://www.mastersofgames.com/rules/reversi-othello-rules.htm)).

Note that it is known that the greedy heuristic of maximizing the number of pieces you have at any given time is a very poor heuristic, making learning more interesting.

To place a piece, one must move the cursor to a valid location on the map and hit fire. The controls are fairly sticky, meaning actions need to be repeated for awhile before they register.

The score is the number of pieces you have on the board. The reward given is the difference is relative reward, so if you flip over 5 pieces of your opponent one turn, you get +6 reward and your opponent gets -6 reward, because you have 6 new pieces (the one you placed plus the 5 you flipped over).

Note that following this reward greedily is known to be a bad long-term strategy, so in order to successfully solve this game, you must think long term.

When one player cannot move, the tokens on both sides are tallied, and the player with the most tokens wins! (receives +1 reward, and their opponent -1).

This is a timed game: if a player does not take a turn after 10 seconds, then that player is rewarded -1 points, their opponent is rewarded nothing, and the timer resets. This prevents one player from indefinitely stalling the game, but also means it is no longer a purely zero sum game.

[Official othello manual](https://atariage.com/manual_html_page.php?SoftwareLabelID=335)

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

* v3: Minimal Action Space (1.18.0)
* v2: Breaking changes to entire API (1.4.0)
* v1: Fixed othello auto reset issue (1.2.1)
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
        game="othello", num_players=2, mode_num=None, env_name=name, **kwargs
    )


env = base_env_wrapper_fn(raw_env)
parallel_env = parallel_wrapper_fn(env)
