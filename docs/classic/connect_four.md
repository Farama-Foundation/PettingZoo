---
actions: "Discrete"
title: "Connect Four"
agents: "2"
manual-control: "No"
action-shape: "(1,)"
action-values: "Discrete(7)"
observation-shape: "(6, 7, 2)"
observation-values: "[0,1]"
import: "from pettingzoo.classic import connect_four_v0"
agent-labels: "agents= ['player_0', 'player_0']"
---

{% include info_box.md %}



Connect Four is a 2-player turn based game, where players must connect four of their tokens vertically, horizontally or diagonally. The players drop their respective token in a column of a standing grid, where each token will fall until it reaches the bottom of the column or reaches an existing token. Players cannot place a token in a full column, and the game ends when either a player has made a sequence of 4 tokens, or when all 7 columns have been filled.

#### Observation Space

The observation space is 2 planes of a 6x7 grid. Each plane represents a specific agent's tokens, and each location in the grid represents the placement of the corresponding agent's token. 1 indicates that the agent has a token placed in that cell, and 0 indicates they do not have a token in that cell. A 0 means that either the cell is empty, or the other agent has a token in that cell.

#### Action Space

The action space is the set of integers from 0 to 6 (inclusive), where the action represents which column a token should be dropped in. If a token is dropped in a column that is full, the game will terminate with an illegal move error. The possible actions each agent can make are stored in `infos[agent]`, and are updated every step.

#### Rewards

If an agent successfully connects four of their tokens, they will be rewarded 1 point. At the same time, the opponent agent will be awarded -1 points. If the game ends in a draw, both players are rewarded 0.

#### Legal Moves

The legal moves available for each agent, found in `env.infos[agent]['legal_moves']`, are updated after each step. Taking an illegal move ends the game with a reward of -1 for the illegally moving agent and a reward of 0 for all other agents.
