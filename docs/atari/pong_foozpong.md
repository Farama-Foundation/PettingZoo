
### Pong: Foozpong

This environment is part of the [Atari environments](../atari.md). Please read that page first for general information.

| Observations | Actions | Agents  | Manual Control | Action Shape | Action Values | Observation Shape | Observation Values | Num States |
|--------------|---------|---------|----------------|--------------|---------------|-------------------|--------------------|------------|
| Graphical    | Discrete  | 4 | No      | (1,)    | [0,17]         | (210, 160, 3)         | (0,255)            | ?          |

`from pettingzoo.atari import pong_foozpong`

`agents= ["first_0", "second_0", "third_0", "fourth_0"]`

![pong_volleyball gif](atari_pong_foozpong.gif)

*AEC diagram*

Four player team battle.

Get the ball past your opponent's defenders to the scoring area. Like foozball, you have alternating layers of players from each team, meaning you need to pass the ball past the defenders to your own team's paddles.

Scoring a point gives your team +1 reward and your opponent team -1 reward.

#### Environment parameters

Some environment parameters are common to all Atari environments and are described in the [base Atari documentation](../atari.md).

Parameters specific to Pong Foozpong are

```
pong_classic.env(num_players=4)
```

```
num_players: Number of players (must be either 2 or 4)
```
