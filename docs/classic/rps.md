---
actions: "Discrete"
title: "Rock Paper Scissors"
agents: "2"
manual-control: "No"
action-shape: "Discrete(3)"
action-values: "Discrete(3)"
observation-shape: "Discrete(4)"
observation-values: "Discrete(4)"
import: "from pettingzoo.classic import rps_v1"
agent-labels: "agents= ['player_0', 'player_1']"
---

{% include info_box.md %}



Rock, Paper, Scissors is a 2-player hand game where each player chooses either rock, paper or scissors and reveals their choices simultaneously. If both players make the same choice, then it is a draw. However, if their choices are different, the winner is determined as follows: rock beats scissors, scissors beat paper, and paper beats rock. 

#### Observation Space

The observation space is a scalar value with 4 possible values. Since both players reveal their choices at the same time, the observation is None until both players have acted. Therefore, 3 represents no action taken yet. Rock is represented with 0, paper with 1 and scissors with 2.

| Value  |  Observation |
| :----: | :---------:  |
| 0      | Rock         |
| 1      | Paper        |
| 2      | Scissors     |
| 3      | None         |

### Action Space

The action space is a scalar value with 3 possible values. The values are encoded as follows: Rock is 0, paper is 1 and scissors is 2.

| Value  |  Action |
| :----: | :---------:  |
| 0      | Rock         |
| 1      | Paper        |
| 2      | Scissors     |

#### Rewards

| Winner | Loser |
| :----: | :---: |
| +1     | -1    |

If the game ends in a draw, both players will receive a reward of 0.
