
### Surround: Original

This environment is part of the [Atari environments](../atari.md). Please read that page first for general information.

| Observations | Actions | Agents  | Manual Control | Action Shape | Action Values | Observation Shape | Observation Values | Num States |
|--------------|---------|---------|----------------|--------------|---------------|-------------------|--------------------|------------|
| Graphical    | Discrete  | 2 | No      | (1,)    | [0,17]         | (210, 160, 3)         | (0,255)            | ?          |

`from pettingzoo.atari import surround_v0`

`agents= ["first_0", "second_0"]`

![surround gif](atari_surround.gif)

*AEC diagram*

A competitive game of planning and strategy.

In surround, your goal is to avoid the walls. If you run into a wall, you are rewarded -1 points, and your opponent, +1 points.

But both players leave a trail of walls behind you, slowly filling the screen with obstacles. To avoid the obstacles as long as possible, you must plan your path to conserve space. Once that is mastered, a higher level aspect of the game comes into play, where both players literally try to surround the other with walls, so their opponent will run out of room and be forced to run into a wall.


#### Environment parameters

Environment parameters are common to all Atari environments and are described in the [base Atari documentation](../atari.md) .
