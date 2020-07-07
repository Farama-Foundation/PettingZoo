
### Entombed: Competitive

This environment is part of the [Atari environments](../atari.md). Please read that page first for general information.

| Observations | Actions | Agents  | Manual Control | Action Shape | Action Values | Observation Shape | Observation Values | Num States |
|--------------|---------|---------|----------------|--------------|---------------|-------------------|--------------------|------------|
| Graphical    | Discrete  | 2 | No      | (1,)    | [0,17]         | (210, 160, 3)         | (0,255)            | ?          |

`from pettingzoo.atari import entombed_competitive_v0`

`agents= ["first_0", "second_0"]`

![entombed_competitive gif](atari_entombed_competitive.gif)

*AEC diagram*


Entomb's competitive version is a race to last the longest.

You need to quickly navigate down a constantly generating
maze you can only see part of. If you get stuck, you lose.
Note you can easily find yourself in a dead-end excapable only through the use of rare power-ups.
In addition, there dangerous zombies lurking around to avoid.
Whenever your opponent dies, you get +1 reward, and your opponent gets -1 reward.


#### Environment parameters

Environment parameters are common to all Atari environments and are described in the [base Atari documentation](../atari.md) .

