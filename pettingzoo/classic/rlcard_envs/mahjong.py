import random

import numpy as np
import rlcard
from gym import spaces

from pettingzoo import AECEnv
from pettingzoo.utils import wrappers

from .rlcard_base import RLCardBase

"""
Mahjong is a tile-based game with 4 players. It uses a deck of 136 tiles that is comprised of 4 identical sets of 34 unique tiles. The objective is to form 4 sets and a pair with the 14th drawn tile. If no player wins, no player receives a reward.

Our implementation wraps [RLCard](http://rlcard.org/games.html#mahjong) and you can refer to its documentation for additional details. Please cite their work if you use this game in research.

### Observation Space
| Plane | Description               |
|:-----:|---------------------------|
|   0   | Current Player's hand     |
|   1   | Played tiles on the table |
|   2   | Public piles of player_0  |
|   3   | Public piles of player_1  |
|   4   | Public piles of player_2  |
|   5   | Public piles of player_3  |

#### Encoding per Plane

| Plane Row Index | Description                                   |
|:---------------:|-----------------------------------------------|
|      0 - 8      | Bamboo<br>_`0`: 1, `1`: 2, ..., `8`: 9_       |
|      9 - 17     | Characters<br>_`9`: 1, `10`: 2, ..., `17`: 9_ |
|     18 - 26     | Dots<br>_`18`: 1, `19`: 2, ..., `26`: 9_      |
|        27       | Dragons Green                                 |
|        28       | Dragons Red                                   |
|        29       | Dragons White                                 |
|        30       | Winds East                                    |
|        31       | Winds West                                    |
|        32       | Winds North                                   |
|        33       | Winds South                                   |

| Plane Column Index | Description |
|:------------------:|-------------|
|          0         | Tile Set 1  |
|          1         | Tile Set 2  |
|          2         | Tile Set 3  |
|          3         | Tile Set 4  |

### Action Space
| Action ID   | Action                                         |
| :---------: | ---------------------------------------------- |
| 0 - 8       | Bamboo<br>_`0`: 1, `1`: 2, ..., `8`: 9_        |
| 9 - 17      | Characters<br>_`9`: 1, `10`: 2, ..., `17`: 9_  |
| 18 - 26     | Dots<br>_`18`: 1, `19`: 2, ..., `26`: 9_       |
| 27          | Dragons Green                                  |
| 28          | Dragons Red                                    |
| 29          | Dragons White                                  |
| 30          | Winds East                                     |
| 31          | Winds West                                     |
| 32          | Winds North                                    |
| 33          | Winds South                                    |
| 34          | Pong                                           |
| 35          | Chow                                           |
| 36          | Gong                                           |
| 37          | Stand                                          |

### Rewards

| Winner | Loser |
| :----: | :---: |
| +1     | -1    |
"""

def env(**kwargs):
    env = raw_env(**kwargs)
    env = wrappers.CaptureStdoutWrapper(env)
    env = wrappers.TerminateIllegalWrapper(env, illegal_reward=-1)
    env = wrappers.AssertOutOfBoundsWrapper(env)
    env = wrappers.OrderEnforcingWrapper(env)
    return env


class raw_env(RLCardBase):

    metadata = {'render.modes': ['human'], "name": "mahjong_v4"}

    def __init__(self):
        super().__init__("mahjong", 4, (6, 34, 4))

    def render(self, mode='human'):
        for player in self.possible_agents:
            state = self.env.game.get_state(self._name_to_int(player))
            print(f"\n======== {player}'s Hand ========")
            print(', '.join([c.get_str() for c in state['current_hand']]))
            print(f"\n{player}'s Piles: ", ', '.join([c.get_str() for pile in state['players_pile'][self._name_to_int(player)] for c in pile]))
        print("\n======== Tiles on Table ========")
        print(', '.join([c.get_str() for c in state['table']]))
        print('\n')
