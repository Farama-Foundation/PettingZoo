
### Boxing

This environment is part of the [Atari environments](../atari.md). Please read that page first for general information.

| Observations | Actions | Agents  | Manual Control | Action Shape | Action Values | Observation Shape | Observation Values | Num States |
|--------------|---------|---------|----------------|--------------|---------------|-------------------|--------------------|------------|
| Graphical    | Discrete  | 2 | No      | (1,)    | [0,17]         | (210, 160, 3)         | (0,255)            | ?          |

`from pettingzoo.atari import boxing_v0`

`agents= ["first_0", "second_0"]`

![boxing gif](atari_boxing.gif)

*AEC diagram*


*Boxing* is an adversarial game where precise control and
appropriate responses to your opponent are key.

The players have two minutes (around 1200 steps) to duke it
out in the ring. Each step, they can move and punch.
Sucessful punches score points,
1 point for a long jab, 2 for a close power punch,
and 100 points for a KO (which also will end the game).
Whenever you score a number of points, you are rewarded by
that number and your opponent is penalized by that number.


#### Environment parameters

Environment parameters are common to all Atari environments and are described in the [base Atari documentation](../atari.md) .

