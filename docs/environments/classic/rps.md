---
actions: "Discrete"
title: "Rock Paper Scissors"
agents: "2"
manual-control: "No"
action-shape: "Discrete(3)"
action-values: "Discrete(3)"
observation-shape: "Discrete(4)"
observation-values: "Discrete(4)"
import: "from pettingzoo.classic import rps_v2"
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




Rock, Paper, Scissors is a 2-player hand game where each player chooses either rock, paper or scissors and reveals their choices simultaneously. If both players make the same choice, then it is a draw. However, if their choices are different, the winner is determined as follows: rock beats scissors, scissors beat paper, and paper beats rock.

The game can be expanded to have extra actions by adding new action pairs. Adding the new actions in pairs allows for a more balanced game. This means that the final game will have an odd number of actions and each action wins over exactly half of the other actions while being defeated by the other half. The most common expansion of this game is [Rock, Paper, Scissors, Lizard, Spock](http://www.samkass.com/theories/RPSSL.html), in which only one extra action pair is added.

### Arguments

``` python
rps_v2.env(num_actions=3, max_cycles=15)
```

`num_actions`:  number of actions applicable in the game. The default value is 3 for the game of Rock, Paper, Scissors. This argument must be an integer greater than 3 and with odd parity. If the value given is 5, the game is expanded to Rock, Paper, Scissors, Lizard, Spock.

`max_cycles`:  after max_cycles steps all agents will return done.

### Observation Space

#### Rock, Paper, Scissors

If 3 actions are required, the game played is the standard Rock, Paper, Scissors. The observation is the last opponent action and its space is a scalar value with 4 possible values. Since both players reveal their choices at the same time, the observation is None until both players have acted. Therefore, 3 represents no action taken yet. Rock is represented with 0, paper with 1 and scissors with 2.

| Value  |  Observation |
| :----: | :---------:  |
| 0      | Rock         |
| 1      | Paper        |
| 2      | Scissors     |
| 3      | None         |

#### Expanded Game

If the number of actions required in the game is greater than 3, the observation is still the last opponent action and its space is a scalar with 1 + n possible values, where n is the number of actions. The observation will as well be None until both players have acted and the largest possible scalar value for the space, 1 + n, represents no action taken yet. The additional actions are encoded in increasing order starting from the 0 Rock action. If 5 actions are required the game is expanded to Rock, Paper, Scissors, Lizard, Spock. The following table shows an example of an observation space with 7 possible actions.   

| Value  |  Observation |
| :----: | :---------:  |
| 0      | Rock         |
| 1      | Paper        |
| 2      | Scissors     |
| 3      | Lizard       |
| 4      | Spock        |
| 5      | Action_6     |
| 6      | Action_7     |
| 7      | None         |

### Action Space

#### Rock, Paper, Scissors

The action space is a scalar value with 3 possible values. The values are encoded as follows: Rock is 0, paper is 1 and scissors is 2.

| Value  |  Action |
| :----: | :---------:  |
| 0      | Rock         |
| 1      | Paper        |
| 2      | Scissors     |

#### Expanded Game

The action space is a scalar value with n possible values, where n is the number of additional action pairs. The values for 7 possible actions are encoded as in the following table.

| Value  |  Action |
| :----: | :---------:  |
| 0      | Rock         |
| 1      | Paper        |
| 2      | Scissors     |
| 3      | Lizard       |
| 4      | Spock        |
| 5      | Action_6     |
| 6      | Action_7     |

### Rewards

| Winner | Loser |
| :----: | :---: |
| +1     | -1    |

If the game ends in a draw, both players will receive a reward of 0.

### Version History

* v2: Merge RPS and rock paper lizard scissors spock environments, add num_actions and max_cycles arguments (1.9.0)
* v1: Bumped version of all environments due to adoption of new agent iteration scheme where all agents are iterated over after they are done (1.4.0)
* v0: Initial versions release (1.0.0)
</div>