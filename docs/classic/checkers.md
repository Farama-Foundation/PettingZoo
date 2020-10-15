---
layout: "docu"
title: "Checkers"
actions: "Discrete"
agents: "2"
manual-control: "No"
action-shape: "Discrete(8*8*4)"
action-values: "Discrete(8*8*4)"
observation-shape: "Box(8, 8, 4)"
observation-values: "[0, 1]"
num-states: "10^21"
import: "from pettingzoo.classic import checkers_v0"
agent-labels: "agents= ['player_0', 'player_1']"

---

{% include info_box.md %}



Checkers (also called Draughts) is a 2-player turn based game. Our implementation is based on the OpenAI gym checkers implementation, with changes to the observation and action spaces.

#### Observation Space

The observation space is 8x8x4 where the first two dimensions represent the row and column on the game board, and the 4 planes in the third dimension represents the type of piece at that location on the board. 

The board is rotated and the planes are shifted to accommodate the current player. During the black player's turn, the top row provided by the `render` function is stored in row 0 of the observation. During the white player's turn, the top row is stored in row 7 of the observation. Additionally, the first two planes of the observation represent the men and kings of the current agent stored in `agent_selection` (The agent that must act next). The last two planes represent the other player's pieces.

| Plane | Observation            |
| ----- | ---------------------- |
| 0     | Current Player's Men   |
| 1     | Current Player's Kings |
| 2     | Other Player's Men     |
| 3     | Other Player's Kings   |

Note that there are only 32 occupiable spaces (the dark colored spaced on a real game board) in the game of checkers. On even numbered rows (starting with 0) the second square is the first occupiable position. On odd numbered rows, the first square is occupiable.

#### Action Space

The action space is a discrete space of size 256 (8 * 8 * 4) discrete values, where each value describes the starting location and direction of a move. The formula `action % 64` returns the action's starting square. The action space can be split into 4 sections of 64 elements as described below:

| Action    | Starting Square | Direction |
| --------- | --------------- | --------- |
| 0...63    | 0...63          | Northwest |
| 64...127  | 0...63          | Northeast |
| 128...191 | 0...63          | Southwest |
| 192...255 | 0...63          | Southeast |

When an action is chosen, the environment automatically decides whether the provided action is a simple move or a jump. Given an action with a starting location and direction, if the square immediately adjacent to the starting location in that direction is unoccupied, then the move is a simple move to that square. If the square is occupied by an enemy man, and the next square in that direction is unoccupied, then the move is a jump. In any other situation, the move is illegal. Note that each player is required to make jumps when available. This is reflected in `infos[agent]['legal moves']` by only listing jump moves if at least one is available.

#### Rewards

| Winner | Loser |
| :----: | :---: |
|   +1   |  -1   |

In the event of a tie, both players receive a reward of 0.

#### Legal Moves

The legal moves available for each agent, found in `env.infos[agent]['legal_moves']`, are updated after each step. Taking an illegal move ends the game with a reward of -1 for the illegally moving agent and a reward of 0 for all other agents.
