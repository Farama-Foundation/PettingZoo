
### Combat: Tank

This environment is part of the [Atari environments](../atari.md). Please read that page first for general information.

| Observations | Actions | Agents  | Manual Control | Action Shape | Action Values | Observation Shape | Observation Values | Num States |
|--------------|---------|---------|----------------|--------------|---------------|-------------------|--------------------|------------|
| Graphical    | Discrete  | 2 | No      | (1,)    | [0,17]         | (210, 160, 3)         | (0,255)            | ?          |

`from pettingzoo.atari import combat_tank_v0`

`agents= ["first_0", "second_0"]`

![combat_tank gif](atari_combat_tank.gif)

*AEC diagram*

*Combat*'s classic tank mode is an adversarial game where prediction, and positioning are key.

The players move around the map. When your opponent is hit by your bullet,
you score a point. Note that your opponent gets blasted through obstacles when it is hit, potentially putting it in a good position to hit you back.

Whenever you score a point, you are rewarded +1 and your opponent is penalized -1.


#### Environment parameters

Some environment parameters are common to all Atari environments and are described in the [base Atari documentation](../atari.md).

Parameters specific to combat-tank are

```
combat_tank.env(has_maze=False, is_invisible=False, billiard_hit=False)
```

```
has_maze: Set to true to have the map be a maze instead of an open field

is_invisible: If true, tanks are invisible unless they are firing or are running into a wall.

billiard_hit: If true, bullets bounce off walls, in fact, like billiards, they only count if they hit the opponent's tank after bouncing off a wall.
```
