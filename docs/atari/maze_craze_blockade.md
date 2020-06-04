
### Maze Craze: Blockade

This environment is part of the [Atari environments](../atari.md). Please read that page first for general information.

| Observations | Actions | Agents  | Manual Control | Action Shape | Action Values | Observation Shape | Observation Values | Num States |
|--------------|---------|---------|----------------|--------------|---------------|-------------------|--------------------|------------|
| Graphical    | Discrete  | 2 | No      | (1,)    | [0,17]         | (210, 160, 3)         | (0,255)            | ?          |

`from pettingzoo.atari import maze_craze_blockade_v0`

`agents= ["first_0", "second_0"]`

![maze_craze_blockade gif](atari_maze_craze_blockade.gif)

*AEC diagram*

A competitive game of memory, planning, and confusion!

Its a race to leave the maze. First, though, you have to capture the robbers, or else you cannot leave (the top of the screen keeps track of which robbers you have captured). Additionally, you can confuse your opponent (and yourself, if you are not careful!) by creating a block that looks identical to a wall in the maze, but all players can pass through it. You can only create one wall at a time, when you create a new one, the old one disappears.

The first player to leave the maze scores +1, the other player scores -1.


#### Environment parameters

Environment parameters are common to all Atari environments and are described in the [base Atari documentation](../atari.md) .
