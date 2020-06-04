
### Maze Craze: Partial visibility

This environment is part of the [Atari environments](../atari.md). Please read that page first for general information.

| Observations | Actions | Agents  | Manual Control | Action Shape | Action Values | Observation Shape | Observation Values | Num States |
|--------------|---------|---------|----------------|--------------|---------------|-------------------|--------------------|------------|
| Graphical    | Discrete  | 2 | No      | (1,)    | [0,17]         | (210, 160, 3)         | (0,255)            | ?          |

`from pettingzoo.atari import maze_craze_partial_vis_v0`

`agents= ["first_0", "second_0"]`

![maze_craze_partial_vis gif](atari_maze_craze_partial_vis.gif)

*AEC diagram*

*BLRB NEEDED!!!*

A competitive game of planning, memory and evasion.

It is a race to exit the maze. But the maze is partially invisible most of the time! Both players have the ability to reveal the maze from time to time, but note that the maze is shown to both players, and this ability has a significant cooldown anyways, so this ability should be used carefully. However, part of the maze is visible all the time. Perhaps the players can use this to augment their idea of the map. In addition, they need to avoid the robbers, who move randomly through the maze. Be careful not to be trapped and get caught by the robbers!

When a player is caught by the robber, they are done, and receive -1 score.

If one escapes successfully, then they get +1 score, their opponent gets -1 score (if they have not already been caught by the robber).


#### Environment parameters

Environment parameters are common to all Atari environments and are described in the [base Atari documentation](../atari.md) .
