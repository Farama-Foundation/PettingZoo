
### Entombed: Cooperative

This environment is part of the [Atari environments](../atari.md). Please read that page first for general information.

| Observations | Actions | Agents  | Manual Control | Action Shape | Action Values | Observation Shape | Observation Values | Num States |
|--------------|---------|---------|----------------|--------------|---------------|-------------------|--------------------|------------|
| Graphical    | Discrete  | 2 | No      | (1,)    | [0,17]         | (210, 160, 3)         | (0,255)            | ?          |

`from pettingzoo.atari import entombed_cooperative_v0`

`agents= ["first_0", "second_0"]`

![entombed_cooperative gif](atari_entombed_cooperative.gif)

*AEC diagram*


Entomb's cooperative version is an exploration game
where you need to work with your teammate to make it
as far as possible into the maze.

You both need to quickly navigate down a constantly generating
maze you can only see part of. If you get stuck, you lose.
Note you can easily find yourself in a dead-end excapable only through the use of rare power-ups.
If players help each other by the use of these powerups, they can last longer.
In addition, there dangerous zombies lurking around to avoid.


#### Environment parameters

Environment parameters are common to all Atari environments and are described in the [base Atari documentation](../atari.md) .
