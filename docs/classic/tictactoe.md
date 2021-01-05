---
actions: "Discrete"
title: "Tic Tac Toe"
agents: "2"
manual-control: "No"
action-shape: "(1)"
action-values: "[0, 8]"
observation-shape: "(3, 3, 2)"
observation-values: "[0,1]"
import: "from pettingzoo.classic import tictactoe_v1"
agent-labels: "agents= ['player_1', 'player_2']"
---

{% include info_box.md %}



Tic-tac-toe is a simple turn based strategy game where 2 players, X and O, take turns marking spaces on a 3 x 3 grid. The first player to place 3 of their marks in a horizontal, vertical, or diagonal line is the winner.

### Observation Space

The observation is a dictionary which contains an `'obs'` element which is the usual RL observation described below, and an  `'action_mask'` which holds the legal moves, described in the Legal Actions Mask section.

The main observation is 2 planes of the 3x3 board. The first plane represents the placement of Xs, and the second plane shows the placement of Os. The possible values for each cell are 0 or 1; in the first plane, 1 indicates that an X has been placed in that cell, and 0 indicates that X is not in that cell. Similarly, in the second plane, 1 indicates that an O has been placed in that cell, while 0 indicates that an O has not been placed.

#### Legal Actions Mask

The legal moves available to the current agent are found in the `action_mask` element of the dictionary observation. The `action_mask` is a binary vector where each index of the vector represents whether the action is legal or not. The `action_mask` will be all zeros for any agent except the one whos turn it is. Taking an illegal move ends the game with a reward of -1 for the illegally moving agent and a reward of 0 for all other agents.

### Action Space

Each action from 0 to 8 represents placing either an X or O in the corresponding cell. The cells are indexed as follows:


 ```
0 | 3 | 6
_________

1 | 4 | 7
_________

2 | 5 | 8
 ```

### Rewards

| Winner | Loser |
| :----: | :---: |
| +1     | -1    |

If the game ends in a draw, both players will receive a reward of 0.
