
### Wizard of Wor

This environment is part of the [Atari environments](../atari.md). Please read that page first for general information.

| Observations | Actions | Agents  | Manual Control | Action Shape | Action Values | Observation Shape | Observation Values | Num States |
|--------------|---------|---------|----------------|--------------|---------------|-------------------|--------------------|------------|
| Graphical    | Discrete  | 2 | No      | (1,)    | [0,17]         | (210, 160, 3)         | (0,255)            | ?          |

`from pettingzoo.atari import wizard_of_wor_v0`

`agents= ["first_0", "second_0"]`

![wizard_of_wor gif](atari_wizard_of_wor.gif)

*AEC diagram*

Battling both against NPCs and the other player. Careful timing,
and control is essential, as well as awareness of your opponent.

You score points by hitting the opponent and NPCs with your bullets. Hitting an NPC scores between 200 to 2500 points depending on the NCP, and hitting a player scores 1000 points.

If you get hit by a bullet, you lose a life. When both players lose 3 lives, the game is over.

Note that in addition to the competitive aspect where you benefit from attacking the other player, there is a cooperative aspect to the game where clearing levels means that both players will have more opportunities to score.

#### Environment parameters

Environment parameters are common to all Atari environments and are described in the [base Atari documentation](../atari.md) .
