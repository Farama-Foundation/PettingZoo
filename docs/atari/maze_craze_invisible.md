
### Maze Craze: Invisible

This environment is part of the [Atari environments](../atari.md). Please read that page first for general information.

| Observations | Actions | Agents  | Manual Control | Action Shape | Action Values | Observation Shape | Observation Values | Num States |
|--------------|---------|---------|----------------|--------------|---------------|-------------------|--------------------|------------|
| Graphical    | Discrete  | 2 | No      | (1,)    | [0,17]         | (210, 160, 3)         | (0,255)            | ?          |

`from pettingzoo.atari import maze_craze_invisible_v0`

`agents= ["first_0", "second_0"]`

![maze_craze_invisible gif](atari_maze_craze_invisible.gif)

*AEC diagram*

A competitive game of memory and planning. 

It is a race to exit the maze. But the maze is completely invisible most of the time! Both players have the ability to reveal the maze from time to time, but note that the maze is shown to both players, and this ability has a significant cooldown anyways, so this ability should be used carefully.

The first player to leave the maze scores +1, the other player scores -1.


#### Environment parameters

Environment parameters are common to all Atari environments and are described in the [base Atari documentation](../atari.md) .
