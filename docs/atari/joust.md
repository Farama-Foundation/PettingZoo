
### Joust

This environment is part of the [Atari environments](../atari.md). Please read that page first for general information.

| Observations | Actions | Agents  | Manual Control | Action Shape | Action Values | Observation Shape | Observation Values | Num States |
|--------------|---------|---------|----------------|--------------|---------------|-------------------|--------------------|------------|
| Graphical    | Discrete  | 2 | No      | (1,)    | [0,17]         | (210, 160, 3)         | (0,255)            | ?          |

`from pettingzoo.atari import joust_v0`

`agents= ["first_0", "second_0"]`

![joust gif](atari_joust.gif)

*AEC diagram*


Scoring points in an unforgiving world (mixed-sum game). Careful positioning, timing,
and control is essential, as well as awareness of your opponent.

In Joust, you score points by hitting the opponent and NPCs when
you are above them. If you are below them, you lose a life.
In a game, there are a variety of waves with different enemies
and different point scoring systems. However, expect that you can earn
around 3000 points per wave.


#### Environment parameters

Environment parameters are common to all Atari environments and are described in the [base Atari documentation](../atari.md) .

