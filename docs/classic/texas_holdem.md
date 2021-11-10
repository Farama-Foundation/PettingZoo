---
actions: "Discrete"
title: "Texas Hold'em"
agents: "2"
manual-control: "No"
action-shape: "Discrete(4)"
action-values: "Discrete(4)"
observation-shape: "(72,)"
observation-values: "[0, 1]"
import: "from pettingzoo.classic import texas_holdem_v4"
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


### Arguments

``` python
texas_holdem_v4.env(num_players=2)
```

`num_players`: Sets the number of players in the game. Minimum is 2.

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

The legal moves available to the current agent are found in the `action_mask` element of the dictionary observation. The `action_mask` is a binary vector where each index of the vector represents whether the action is legal or not. The `action_mask` will be all zeros for any agent except the one whose turn it is. Taking an illegal move ends the game with a reward of -1 for the illegally moving agent and a reward of 0 for all other agents.

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

### Version History

* v4: Upgrade to RLCard 1.0.3 (1.11.0)
* v3: Fixed bug in arbitrary calls to observe() (1.8.0)
* v2: Bumped RLCard version, bug fixes, legal action mask in observation replaced illegal move list in infos (1.5.0)
* v1: Bumped RLCard version, fixed observation space, adopted new agent iteration scheme where all agents are iterated over after they are done (1.4.0)
* v0: Initial versions release (1.0.0)
</div>
