---
actions: "Discrete"
title: "Texas Hold'em No Limit"
agents: "2"
manual-control: "No"
action-shape: "Discrete(103)"
action-values: "Discrete(103)"
observation-shape: "(54,)"
observation-values: "[0, 100]"
import: "from pettingzoo.classic import texas_holdem_no_limit_v1"
agent-labels: "agents= ['player_0', 'player_1']"
---

{% include info_box.md %}



Texas Hold'em No Limit is a variation of Texas Hold'em where there is no limit on the amount of each raise or the number of raises.

Our implementation wraps [RLCard](http://rlcard.org/games.html#no-limit-texas-hold-em) and you can refer to its documentation for additional details. Please cite their work if you use this game in research.

### Observation Space

The observation is a dictionary which contains an `'obs'` element which is the usual RL observation described below, and an  `'action_mask'` which holds the legal moves, described in the Legal Actions Mask section.

The main observation space is similar to Texas Hold'em. The first 52 entries represent the union of the current player's hand and the community cards.

|  Index  | Description                                  |  Values  |
|:-------:|----------------------------------------------|:--------:|
|  0 - 12 | Spades<br>_`0`: A, `1`: 2, ..., `12`: K_     |  [0, 1]  |
| 13 - 25 | Hearts<br>_`13`: A, `14`: 2, ..., `25`: K_   |  [0, 1]  |
| 26 - 38 | Diamonds<br>_`26`: A, `27`: 2, ..., `38`: K_ |  [0, 1]  |
| 39 - 51 | Clubs<br>_`39`: A, `40`: 2, ..., `51`: K_    |  [0, 1]  |
|    52   | Number of Chips of player_0                  | [0, 100] |
|    53   | Number of Chips of player_1                  | [0, 100] |

#### Legal Actions Mask

The legal moves available to the current agent are found in the `action_mask` element of the dictionary observation. The `action_mask` is a binary vector where each index of the vector represents whether the action is legal or not. The `action_mask` will be all zeros for any agent except the one whos turn it is. Taking an illegal move ends the game with a reward of -1 for the illegally moving agent and a reward of 0 for all other agents.

### Action Space

| Action ID | Action                                                      |
|:---------:|-------------------------------------------------------------|
|     0     | Call                                                        |
|     1     | Raise                                                       |
|     2     | Check                                                       |
|  3 - 102  | Raise<br>_`3`: 1 chip, `4`: 2 chips, ..., `102`: 100 chips_ |

### Rewards

| Winner          | Loser           |
| :-------------: | :-------------: |
| +raised chips/2 | -raised chips/2 |
