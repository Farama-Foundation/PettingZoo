
### Connect Four

This game part of the [classic games](../classic.md), please visit that page first for general information about these games.

| Actions  | Agents | Manual Control | Action Shape  | Action Values  | Observation Shape | Observation Values | Num States    |
|----------|--------|----------------|---------------|----------------|-------------------|--------------------|---------------|
| Discrete | 2      | No             | (1,)          | Discrete(7)    | (6, 7, 2)         | [0,1]              |   ?           |

`from pettingzoo.classic import connect_four_v0`

`agents= ['player_0', 'player_0']`

![](classic_connect_four.gif)

*AEC Diagram*

Connect Four is a 2 player turn based game, where players must connect four of their tokens vertically, horizontally or diagonally. The players drop their respective token in a standing grid, where each token will fall as far down into its column as possible. Players cannot fill up a column with more than 6 token, and the game ends when either a player has made a sequence of 4 token, or when all 7 columns have been filled.

#### Observation Space

The observation space is 2 stacks of a 6x7 grid. Each stack represents the placement of the corresponding agent's token, where 1 indicates that the agent has a token placed in that cell, and 0 means they do not have a token in that cell. 0 can be interpreted as either the cell being empty, or the other agent may have a token in that cell.

#### Action Space

The action space is integers from 0 to 6, where the action represents which column a token should be dropped in. If a token is dropped in a column that is full, the game will terminate with an illegal move error. The possible actions each agent can make is stored in infos[agent], and is updated on every step.

#### Rewards

If an agent successfully connects four of their tokens, they will be rewarded 1 point. At the same time, the opponent agent will be awarded -1 points. If the game ends in a draw, both players are rewarded 0.

#### Legal Moves

The legal moves available for each agent, found in `env.infos[agent]['legal_moves']`, are updated after each step. Taking an illegal move ends the game with a reward of -1 for the illegally moving agent and a reward of 0 for all other agents.
