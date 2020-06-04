
### Ice Hockey

This environment is part of the [Atari environments](../atari.md). Please read that page first for general information.

| Observations | Actions | Agents  | Manual Control | Action Shape | Action Values | Observation Shape | Observation Values | Num States |
|--------------|---------|---------|----------------|--------------|---------------|-------------------|--------------------|------------|
| Graphical    | Discrete  | 2 | No      | (1,)    | [0,17]         | (210, 160, 3)         | (0,255)            | ?          |

`from pettingzoo.atari import ice_hockey_v0`

`agents= ["first_0", "second_0"]`

![ice_hockey gif](atari_ice_hockey.gif)

*AEC diagram*

Competitive game of control and timing.

When you are on offense you must pass the puck between your two players (you control the one with the puck) to get it past your opponent's defense. On defense, you control the player directly in front of the puck. Both players must handle the rapid switches of control, while maneuvering around your opponent. If you score, you are rewarded +1, and your opponent -1.



#### Environment parameters

Environment parameters are common to all Atari environments and are described in the [base Atari documentation](../atari.md) .
