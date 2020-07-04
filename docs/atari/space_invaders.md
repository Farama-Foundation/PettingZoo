
### Space Invaders

This environment is part of the [Atari environments](../atari.md). Please read that page first for general information.

| Observations | Actions | Agents  | Manual Control | Action Shape | Action Values | Observation Shape | Observation Values | Num States |
|--------------|---------|---------|----------------|--------------|---------------|-------------------|--------------------|------------|
| Graphical    | Discrete  | 2 | No      | (1,)    | [0,17]         | (210, 160, 3)         | (0,255)            | ?          |

`from pettingzoo.atari import space_invaders_v0`

`agents= ["first_0", "second_0"]`

![space_invaders_easy gif](atari_space_invaders.gif)

*AEC diagram*

Classic Atari game, but there are two ships controlled by two players that are each trying to maximize their score.

This game has a cooperative aspect where the players can choose to maximize their score by working together to clear the levels. The normal aliens are 5-30 points, depending on how high up they start, and the ship that flies across the top of the screen is worth 100 points.

However, there is also a competitive aspect where a player receives a 200 point bonus when the other player is hit by the aliens. So sabotaging the other player somehow is a possible strategy.

The number of lives is shared between the ships, i.e. the game ends when a ship has been hit 3 times.

#### Environment parameters

Some environment parameters are common to all Atari environments and are described in the [base Atari documentation](../atari.md).

Parameters specific to Space Invaders are

```
space_invaders.env(alternating_control=False, moving_shields=True, zigzaging_bombs=False, fast_bomb=False, invisible_invaders=False)
```

```
alternating_control: Only one of the two players has an option to fire at one time. If you fire, your opponent can then fire. However, you can't hoard the firing ability forever, eventually, control shifts to your opponent anyways.

moving_shields: The shields move back and forth, leaving less reliable protection.

zigzaging_bombs: The invader's bombs move back and forth, making them more difficult to avoid.

fast_bomb: The bombs are much faster, making them more difficult to avoid.

invisible_invaders: The invaders are invisible, making them more difficult to hit.
```
