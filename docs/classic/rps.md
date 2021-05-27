---
actions: "Discrete"
title: "Rock Paper Scissors"
agents: "2"
manual-control: "No"
action-shape: "Discrete(3),(5)"
action-values: "Discrete(3),(5)"
observation-shape: "Discrete(4),(6)"
observation-values: "Discrete(4),(6)"
import: "from pettingzoo.classic import rps_v1"
agent-labels: "agents= ['player_0', 'player_1']"
---

{% include info_box.md %}



Rock, Paper, Scissors is a 2-player hand game where each player chooses either rock, paper or scissors and reveals their choices simultaneously. If both players make the same choice, then it is a draw. However, if their choices are different, the winner is determined as follows: rock beats scissors, scissors beat paper, and paper beats rock.

The game can be expanded to Rock Paper, Scissors, Lizard, Spock. Rock, Paper, Scissors, Lizard, Spock is a variation of the traditional Rock Paper Scissors game, where the choices lizard and Spock are added as well. The interactions between Rock, Paper and Scissor are the same as the original with Rock beating scissors, scissors beating paper and paper beating rock. However, the new choices interact as follows: rock crushes lizard, lizard poisons Spock, Spock smashes scissors, scissors beats lizard, lizard eats paper, paper beats Spock, and Spock destroys rock. As is in the original, each player reveal their choice at the same time, at which point the winner is determined.

### Arguments

```
pistonball.env(lizard_spock=False, max_cycles=150)
```

`lizard_spock`:  Expands the game to Rock, Paper, Scissors, Lizard, Spock if True. Default False

`max_cycles`:  after max_cycles steps all agents will return done.

### Observation Space

#### Rock, Paper, Scissors

If the game played is Rock, Paper, Scissors, the observation is the last oppoent action and its space is a scalar value with 4 possible values. Since both players reveal their choices at the same time, the observation is None until both players have acted. Therefore, 3 represents no action taken yet. Rock is represented with 0, paper with 1 and scissors with 2.

| Value  |  Observation |
| :----: | :---------:  |
| 0      | Rock         |
| 1      | Paper        |
| 2      | Scissors     |
| 3      | None         |

#### Paper, Scissors, Lizard, Spock

If the game played is Paper, Scissors, Lizard, Spock, the observation is the last opponent action and its space is a scalar value with 6 possible values. Since both players reveal their choices at the same time, the observation is None until both players have acted. Therefore, 5 represents no action taken yet. Rock is represented with 0, paper with 1, scissors with 2, lizard with 3, and Spock with 4.

| Value  |  Observation |
| :----: | :---------:  |
| 0      | Rock         |
| 1      | Paper        |
| 2      | Scissors     |
| 3      | Lizard       |
| 4      | Spock        |
| 5      | None         |

### Action Space

#### Rock, Paper, Scissors

The action space is a scalar value with 3 possible values. The values are encoded as follows: Rock is 0, paper is 1 and scissors is 2.

| Value  |  Action |
| :----: | :---------:  |
| 0      | Rock         |
| 1      | Paper        |
| 2      | Scissors     |

#### Paper, Scissors, Lizard, Spock

The action space is a scalar value with 5 possible values. The values are encoded as follows: Rock is 0, paper is 1, scissors is 2, lizard is 3, and Spock is 4.

| Value  |  Action |
| :----: | :---------:  |
| 0      | Rock         |
| 1      | Paper        |
| 2      | Scissors     |
| 3      | Lizard       |
| 4      | Spock        |

### Rewards

| Winner | Loser |
| :----: | :---: |
| +1     | -1    |

If the game ends in a draw, both players will receive a reward of 0.
