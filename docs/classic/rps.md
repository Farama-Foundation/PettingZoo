
### Rock Paper Scissors

This game part of the [classic games](../classic.md), please visit that page first for general information about these games.

| Actions | Agents | Manual Control | Action Shape | Action Values | Observation Shape | Observation Values | Num States |
|----------|---------|----------------|--------------|---------------|-------------------|--------------------|------------|
| ?            | ?       | ?      | ?              | ?            | ?             | ?                 | ?                  | ?          |

`from pettingzoo.classic import rps_v0`

`agents= `

![](classic_rps.gif)

*AEC Diagram*

*Blurb*

#### Rewards

| Winner | Loser |
| :----: | :---: |
| +1     | -1    |

If the game ends in a draw, both players will receive a reward of 0.
