---
layout: "docu"
title: "Backgammon"
actions: "Discrete"
agents: "2"
manual-control: "No"
action-shape: "Discrete(32,4)"
action-values: "Discrete(32)"
observation-shape: "(32,4)"
observation-values: "[0, 1]"
num-states: "10^21"
import: "from pettingzoo.classic import checkers_v0"
agent-labels: "agents= ['player_0', 'player_1']"

---

{% include info_box.md %}



Checkers (also claled Draughts) is a 2-player turn based game. Our implementation is based on the OpenAI gym checkers implementation, with changes to the observation and action spaces.

#### Observation Space

There are 32 habitable spaces in the game of checkers, numbered from left to right and top to bottom, such that every other square in a row is numbered. On even numbered rows (starting with 0) the second square is the first habitable position. On odd numbered rows, the first square is habitable.

The observation contains 4 planes, each which indicate the presence of a specific type of piece in the habitable locations of the board



| Plane | Observation |
| ----- | ----------- |
| 0     | Black Men   |
| 1     | Black Kings |
| 2     | White Men   |
| 3     | White Kings |

#### Action Space

The action space is also divided into 4 planes, one for each direction that a piece can move. Each plane has 32 values, one for each habitable square on the board. The action directions listed below:

| Action | Direction |
| ------ | --------- |
| 0      | Northwest |
| 1      | Northeast |
| 2      | Southwest |
| 3      | Southeast |

The environment automatically decides whether the provided action is a simple move or a jump. Note that jumps are required when available. This is reflected in `infos[agent]['legal moves']` by listing jump moves and no simple moves if jumps are available.

#### Rewards

| Winner | Loser |
| :----: | :---: |
|   +1   |  -1   |


#### Legal Moves

The legal moves available for each agent, found in `env.infos[agent]['legal_moves']`, are updated after each step. Taking an illegal move ends the game with a reward of -1 for the illegally moving agent and a reward of 0 for all other agents.