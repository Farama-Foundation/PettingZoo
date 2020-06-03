
### Double Dunk

This environment is part of the [Atari environments](../atari.md). Please read that page first for general information.

| Observations | Actions | Agents  | Manual Control | Action Shape | Action Values | Observation Shape | Observation Values | Num States |
|--------------|---------|---------|----------------|--------------|---------------|-------------------|--------------------|------------|
| Graphical    | Discrete  | 2 | No      | (1,)    | [0,17]         | (210, 160, 3)         | (0,255)            | ?          |

`from pettingzoo.atari import double_dunk_v0`

`agents= ["first_0", "second_0"]`

![double_dunk gif](atari_double_dunk.gif)

*AEC diagram*


An adversarial game that combines control and precise selection.

The game has two stages: selection and play. Selection can be
difficult because you have to hold the same action for a few steps and then
take the 0 action. Also, since both players have to select a play
in order for play to resume, there is possiblity of learning to
stall by not selecting anything.
Once play begins, each team has two players. You only control
one at a time, and and which one you control depends on the selected play.
Scoring should be familar to basketball fans (2-3 points per successful shot).


#### Environment parameters

Environment parameters are common to all Atari environments and are described in the [base Atari documentation](../atari.md) .

