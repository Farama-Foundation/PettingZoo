
### Mario Bros

This environment is part of the [Atari environments](../atari.md). Please read that page first for general information.

| Observations | Actions | Agents  | Manual Control | Action Shape | Action Values | Observation Shape | Observation Values | Num States |
|--------------|---------|---------|----------------|--------------|---------------|-------------------|--------------------|------------|
| Graphical    | Discrete  | 2 | No      | (1,)    | [0,17]         | (210, 160, 3)         | (0,255)            | ?          |

`from pettingzoo.atari import mario_bros_v0`

`agents= ["first_0", "second_0"]`

![mario_bros gif](atari_mario_bros.gif)

*AEC diagram*

A mixed-sum game of control and timing.

Collect points and avoid obstacles with another player in the same space.

Rewards are received by completing various tasks that give either 500 or 800 points.

#### Environment parameters

Environment parameters are common to all Atari environments and are described in the [base Atari documentation](../atari.md) .
