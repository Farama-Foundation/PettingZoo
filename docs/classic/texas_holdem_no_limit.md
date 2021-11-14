---
actions: "Discrete"
title: "Texas Hold'em No Limit"
agents: "2"
manual-control: "No"
action-shape: "Discrete(5)"
action-values: "Discrete(5)"
observation-shape: "(54,)"
observation-values: "[0, 100]"
import: "from pettingzoo.classic import texas_holdem_no_limit_v6"
agent-labels: "agents= ['player_0', 'player_1']"
---

<div class="docu-info" markdown="1">
{% include info_box.md %}
</div>

<div class="docu-content" markdown="1">
<div class="appear_big env-title" markdown="1">
{% include env_icon.md %}
## {{page.title}}
</div>


Texas Hold'em No Limit is a variation of Texas Hold'em where there is no limit on the amount of each raise or the number of raises.

Our implementation wraps [RLCard](http://rlcard.org/games.html#no-limit-texas-hold-em) and you can refer to its documentation for additional details. Please cite their work if you use this game in research.

### Arguments

``` python
texas_holdem_no_limit_v6.env(num_players=2)
```

`num_players`: Sets the number of players in the game. Minimum is 2.


Texas Hold'em is a poker game involving 2 players and a regular 52 cards deck. At the beginning, both players get two cards. After betting, three community cards are shown and another round follows. At any time, a player could fold and the game will end. The winner will receive +1 as a reward and the loser will get -1. This is an implementation of the standard limited version of Texas Hold'm, sometimes referred to as 'Limit Texas Hold'em'.

Our implementation wraps [RLCard](http://rlcard.org/games.html#limit-texas-hold-em) and you can refer to its documentation for additional details. Please cite their work if you use this game in research.


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

The legal moves available to the current agent are found in the `action_mask` element of the dictionary observation. The `action_mask` is a binary vector where each index of the vector represents whether the action is legal or not. The `action_mask` will be all zeros for any agent except the one whose turn it is. Taking an illegal move ends the game with a reward of -1 for the illegally moving agent and a reward of 0 for all other agents.

### Action Space

| Action ID   |     Action         |
| ----------- | :----------------- |
| 0           | Fold               |
| 1           | Check & Call       |
| 2           | Raise Half Pot     |
| 3           | Raise Full Pot     |
| 4           | All In             |

### Rewards

| Winner          | Loser           |
| :-------------: | :-------------: |
| +raised chips/2 | -raised chips/2 |

### Version History

* v6: Upgrade to RLCard 1.0.5, fixes to the action space as ACPC (1.12.0)
* v5: Upgrade to RLCard 1.0.4, fixes to rewards with greater than 2 players (1.11.1)
* v4: Upgrade to RLCard 1.0.3 (1.11.0)
* v3: Fixed bug in arbitrary calls to observe() (1.8.0)
* v2: Bumped RLCard version, bug fixes, legal action mask in observation replaced illegal move list in infos (1.5.0)
* v1: Bumped RLCard version, fixed observation space, adopted new agent iteration scheme where all agents are iterated over after they are done (1.4.0)
* v0: Initial versions release (1.0.0)
</div>