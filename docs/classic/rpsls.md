---
actions: "Discrete"
title: "Rock Paper Scissors Lizard Spock"
agents: "2"
manual-control: "No"
action-shape: "Discrete(5)"
action-values: "Discrete(5)"
observation-shape: "Discrete(6)"
observation-values: "Discrete(6)"
import: "from pettingzoo.classic import rpsls_v1"
agent-labels: "agents= ['player_0', 'player_1']"
---
{% include info_box.md %}



Rock Paper Scissors Lizard Spock is a variation of the traditional Rock Paper Scissors game, where the choices lizard and Spock are added as well. The interactions between Rock, Paper and Scissor are the same as the original with Rock beating scissors, scissors beating paper and paper beating rock. However, the new choices interact as follows: rock crushes lizard, lizard poisons Spock, Spock smashes scissors, scissors beats lizard, lizard eats paper, paper beats Spock, and Spock destroys rock. As is in the original, each player reveal their choice at the same time, at which point the winner is determined.


#### Observation Space

The observation space is a scalar value with 6 possible values. Since both players reveal their choices at the same time, the observation is None until both players have acted. Therefore, 5 represents no action taken yet. Rock is represented with 0, paper with 1, scissors with 2, lizard with 3, and Spock with 4.

| Value  |  Observation |
| :----: | :---------:  |
| 0      | Rock         |
| 1      | Paper        |
| 2      | Scissors     |
| 3      | Lizard       |
| 4      | Spock        |
| 5      | None         |

### Action Space

The action space is a scalar value with 5 possible values. The values are encoded as follows: Rock is 0, paper is 1, scissors is 2, lizard is 3, and Spock is 4.

| Value  |  Action |
| :----: | :---------:  |
| 0      | Rock         |
| 1      | Paper        |
| 2      | Scissors     |
| 3      | Lizard       |
| 4      | Spock        |

#### Rewards

| Winner | Loser |
| :----: | :---: |
| +1     | -1    |

If the game ends in a draw, both players will receive a reward of 0.