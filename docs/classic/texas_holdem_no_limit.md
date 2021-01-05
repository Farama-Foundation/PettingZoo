---
actions: "Discrete"
title: "Texas Hold'em"
agents: "2"
manual-control: "No"
action-shape: "Discrete(4)"
action-values: "Discrete(4)"
observation-shape: "(72,)"
observation-values: "[0, 1]"
import: "from pettingzoo.classic import texas_holdem_v1"
agent-labels: "agents= ['player_0', 'player_1']"
---

{% include info_box.md %}



Texas Hold'em is a poker game involving 2 players and a regular 52 cards deck. At the beginning, both players get two cards. After betting, three community cards are shown and another round follows. At any time, a player could fold and the game will end. The winner will receive +1 as a reward and the loser will get -1. This is an implementation of the standard limitted version of Texas Hold'm, sometimes referred to as 'Limit Texas Hold'em'.

Our implementation wraps [RLCard](http://rlcard.org/games.html#limit-texas-hold-em) and you can refer to its documentation for additional details. Please cite their work if you use this game in research.


### Observation Space

The observation is a dictionary which contains an `'obs'` element which is the usual RL observation described below, and an  `'action_mask'` which holds the legal moves, described in the Legal Actions Mask section.

The main observation space is a vector of 72 boolean integers. The first 52 entries depict the current player's hand plus any community cards as follows

|  Index  | Description                                                 |
|:-------:|-------------------------------------------------------------|
|  0 - 12 | Spades<br>_`0`: A, `1`: 2, ..., `12`: K_                    |
| 13 - 25 | Hearts<br>_`13`: A, `14`: 2, ..., `25`: K_                  |
| 26 - 38 | Diamonds<br>_`26`: A, `27`: 2, ..., `38`: K_                |
| 39 - 51 | Clubs<br>_`39`: A, `40`: 2, ..., `51`: K_                   |
| 52 - 56 | Chips raised in Round 1<br>_`52`: 0, `53`: 1, ..., `56`: 4_ |
| 57 - 61 | Chips raised in Round 2<br>_`57`: 0, `58`: 1, ..., `61`: 4_ |
| 62 - 66 | Chips raised in Round 3<br>_`62`: 0, `63`: 1, ..., `66`: 4_ |
| 67 - 71 | Chips raised in Round 4<br>_`67`: 0, `68`: 1, ..., `71`: 4_ |

#### Legal Actions Mask

The legal moves available to the current agent are found in the `action_mask` element of the dictionary observation. The `action_mask` is a binary vector where each index of the vector represents whether the action is legal or not. The `action_mask` will be all zeros for any agent except the one whos turn it is. Taking an illegal move ends the game with a reward of -1 for the illegally moving agent and a reward of 0 for all other agents.

### Action Space

| Action ID | Action |
|:---------:|--------|
|     0     | Call   |
|     1     | Raise  |
|     2     | Fold   |
|     3     | Check  |

### Rewards

| Winner          | Loser           |
| :-------------: | :-------------: |
| +raised chips/2 | -raised chips/2 |
