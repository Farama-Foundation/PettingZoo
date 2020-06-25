
### Pong: Classic

This environment is part of the [Atari environments](../atari.md). Please read that page first for general information.

| Observations | Actions | Agents  | Manual Control | Action Shape | Action Values | Observation Shape | Observation Values | Num States |
|--------------|---------|---------|----------------|--------------|---------------|-------------------|--------------------|------------|
| Graphical    | Discrete  | 2 | No      | (1,)    | [0,17]         | (210, 160, 3)         | (0,255)            | ?          |

`from pettingzoo.atari import pong_classic_v0`

`agents= ["first_0", "second_0"]`

![pong gif](atari_pong_classic.gif)

*AEC diagram*

Classic two player competitive game of timing.

Get the ball past the opponent.

Scoring a point gives you +1 reward and your opponent -1 reward.


#### Environment parameters

Some environment parameters are common to all Atari environments and are described in the [base Atari documentation](../atari.md).

Parameters specific to Pong Classic are

```
pong_classic.env(num_players=2)
```

```
num_players: Number of players (must be either 2 or 4)
```
