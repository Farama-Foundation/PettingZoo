---
actions: "Discrete"
title: "Mahjong"
agents: "4"
manual-control: "No"
action-shape: "Discrete(38)"
action-values: "Discrete(38)"
observation-shape: "(6, 34, 4)"
observation-values: "[0, 1]"
import: "from pettingzoo.classic import mahjong_v4"
agent-labels: "agents= ['player_0', 'player_1', 'player_2', 'player_3']"
---
<div class="docu-info" markdown="1">
{% include info_box.md %}
</div>

<div class="docu-content" markdown="1">
<div class="appear_big env-title" markdown="1">
{% include env_icon.md %}
## {{page.title}}
</div>




Mahjong is a tile-based game with 4 players. It uses a deck of 136 tiles that is comprised of 4 identical sets of 34 unique tiles. The objective is to form 4 sets and a pair with the 14th drawn tile. If no player wins, no player receives a reward.

Our implementation wraps [RLCard](http://rlcard.org/games.html#mahjong) and you can refer to its documentation for additional details. Please cite their work if you use this game in research.



### Observation Space

The observation is a dictionary which contains an `'obs'` element which is the usual RL observation described below, and an  `'action_mask'` which holds the legal moves, described in the Legal Actions Mask section.


The main observation space has a (6, 34, 4) shape with the first index representing the encoding plane. The contents of each plane are described in the table below:

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

#### Legal Actions Mask

The legal moves available to the current agent are found in the `action_mask` element of the dictionary observation. The `action_mask` is a binary vector where each index of the vector represents whether the action is legal or not. The `action_mask` will be all zeros for any agent except the one whose turn it is. Taking an illegal move ends the game with a reward of -1 for the illegally moving agent and a reward of 0 for all other agents.

### Action Space

The action space, as described by RLCard, is

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

For example, you would use action `34` to pong or action `37` to stand.

### Rewards

| Winner | Loser |
| :----: | :---: |
| +1     | -1    |

### Version History

* v4: Upgrade to RLCard 1.0.3 (1.11.0)
* v3: Fixed bug in arbitrary calls to observe() (1.8.0)
* v2: Bumped RLCard version, bug fixes, legal action mask in observation replaced illegal move list in infos (1.5.0)
* v1: Bumped RLCard version, fixed observation space, adopted new agent iteration scheme where all agents are iterated over after they are done (1.4.0)
* v0: Initial versions release (1.0.0)
</div>