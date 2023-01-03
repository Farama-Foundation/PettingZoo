# noqa
"""
# Leduc Hold'em

```{figure} classic_leduc_holdem.gif
:width: 140px
:name: leduc_holdem
```

This environment is part of the <a href='..'>classic environments</a>. Please read that page first for general information.

| Import             | `from pettingzoo.classic import leduc_holdem_v4` |
|--------------------|--------------------------------------------------|
| Actions            |                                                  |
| Parallel API       | Yes                                              |
| Manual Control     | No                                               |
| Agents             | `agents= ['player_0', 'player_1']`               |
| Agents             | 2                                                |
| Action Shape       | Discrete(4)                                      |
| Action Values      | Discrete(4)                                      |
| Observation Shape  | (36,)                                            |
| Observation Values | [0, 1]                                           |


Leduc Hold'em is a variation of Limit Texas Hold'em with 2 players, 2 rounds and a deck of six cards (Jack, Queen, and King in 2 suits). At the beginning of the game, each player receives one card and, after betting, one public card is revealed. Another round follow. At the end, the player with
the best hand wins and receives a reward (+1) and the loser receives -1. At any time, any player can fold.

Our implementation wraps [RLCard](http://rlcard.org/games.html#leduc-hold-em) and you can refer to its documentation for additional details. Please cite their work if you use this game in research.

### Arguments

``` python
leduc_holdem_v4.env(num_players=2)
```

`num_players`: Sets the number of players in the game. Minimum is 2.

### Observation Space

The observation is a dictionary which contains an `'observation'` element which is the usual RL observation described below, and an  `'action_mask'` which holds the legal moves, described in the Legal Actions Mask section.

As described by [RLCard](https://github.com/datamllab/rlcard/blob/master/docs/games#leduc-holdem), the first 3 entries of the main observation space correspond to the player's hand (J, Q, and K) and the next 3 represent the public cards. Indexes 6 to 19 and 20 to 33 encode the number of chips by
the current player and the opponent, respectively.

|  Index  | Description                                                                  |
|:-------:|------------------------------------------------------------------------------|
|  0 - 2  | Current Player's Hand<br>_`0`: J, `1`: Q, `2`: K_                            |
|  3 - 5  | Community Cards<br>_`3`: J, `4`: Q, `5`: K_                                  |
|  6 - 20 | Current Player's Chips<br>_`6`: 0 chips, `7`: 1 chip, ..., `20`: 14 chips_   |
| 21 - 35 | Opponent's Chips<br>_`21`: 0 chips, `22`: 1 chip, ..., `35`: 14 chips_       |


#### Legal Actions Mask

The legal moves available to the current agent are found in the `action_mask` element of the dictionary observation. The `action_mask` is a binary vector where each index of the vector represents whether the action is legal or not. The `action_mask` will be all zeros for any agent except the one
whose turn it is. Taking an illegal move ends the game with a reward of -1 for the illegally moving agent and a reward of 0 for all other agents.

### Action Space

| Action ID | Action |
|:---------:|--------|
|     0     | Call   |
|     1     | Raise  |
|     2     | Fold   |
|     3     | Check  |

### Rewards

|      Winner       |       Loser       |
| :---------------: | :---------------: |
| +raised chips / 2 | -raised chips / 2 |


### Version History

* v4: Upgrade to RLCard 1.0.3 (1.11.0)
* v3: Fixed bug in arbitrary calls to observe() (1.8.0)
* v2: Bumped RLCard version, bug fixes, legal action mask in observation replaced illegal move list in infos (1.5.0)
* v1: Bumped RLCard version, fixed observation space, adopted new agent iteration scheme where all agents are iterated over after they are done (1.4.0)
* v0: Initial versions release (1.0.0)

"""

import gymnasium
from rlcard.utils.utils import print_card

from pettingzoo.utils import wrappers

from .rlcard_base import RLCardBase


def env(**kwargs):
    render_mode = kwargs.get("render_mode")
    if render_mode == "ansi":
        kwargs["render_mode"] = "human"
        env = raw_env(**kwargs)
        env = wrappers.CaptureStdoutWrapper(env)
    else:
        env = raw_env(**kwargs)
    env = wrappers.TerminateIllegalWrapper(env, illegal_reward=-1)
    env = wrappers.AssertOutOfBoundsWrapper(env)
    env = wrappers.OrderEnforcingWrapper(env)
    return env


class raw_env(RLCardBase):

    metadata = {
        "render_modes": ["human"],
        "name": "leduc_holdem_v4",
        "is_parallelizable": False,
        "render_fps": 1,
    }

    def __init__(self, num_players=2, render_mode=None):
        super().__init__("leduc-holdem", num_players, (36,))
        self.render_mode = render_mode

    def render(self):
        if self.render_mode is None:
            gymnasium.logger.warn(
                "You are calling render method without specifying any render mode."
            )
            return

        for player in self.possible_agents:
            state = self.env.game.get_state(self._name_to_int(player))
            print(f"\n=============== {player}'s Hand ===============")
            print_card(state["hand"])
            print("\n{}'s Chips: {}".format(player, state["my_chips"]))
        print("\n================= Public Cards =================")
        print_card(state["public_card"]) if state["public_card"] is not None else print(
            "No public cards."
        )
        print("\n")
