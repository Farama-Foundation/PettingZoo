
### Combat: Jet

This environment is part of the [Atari environments](../atari.md). Please read that page first for general information.

| Observations | Actions | Agents  | Manual Control | Action Shape | Action Values | Observation Shape | Observation Values | Num States |
|--------------|---------|---------|----------------|--------------|---------------|-------------------|--------------------|------------|
| Graphical    | Discrete  | 2 | No      | (1,)    | [0,17]         | (210, 160, 3)         | (0,255)            | ?          |

`from pettingzoo.atari import combat_jet_v0`

`agents= ["first_0", "second_0"]`

![combat_jet gif](atari_combat_plane.gif)

*AEC diagram*


*Combat*'s plane mode is an adversarial game where timing,
positioning, and keeping track of your opponent's complex
movements are key.

The players fly around the map, able to control flight direction
but not your speed.

When your opponent is hit by your bullet,
you score a point.

Whenever you score a point, you are rewarded +1 and your opponent is penalized -1.


#### Environment parameters

Some environment parameters are common to all Atari environments and are described in the [base Atari documentation](../atari.md).

Parameters specific to combat-plane are

```
combat_plane.env(is_jet=False, guided_missile=False)
```

```
is_jet: Whether the plane is a bi-plane or a jet. (Jets move faster)

guided_missile: Whether the missile can be directed after being fired, or whether it is on a fixed path.
```
