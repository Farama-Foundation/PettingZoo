
### Flag Capture

This environment is part of the [Atari environments](../atari.md). Please read that page first for general information.

| Observations | Actions | Agents  | Manual Control | Action Shape | Action Values | Observation Shape | Observation Values | Num States |
|--------------|---------|---------|----------------|--------------|---------------|-------------------|--------------------|------------|
| Graphical    | Discrete  | 2 | No      | (1,)    | [0,17]         | (210, 160, 3)         | (0,255)            | ?          |

`from pettingzoo.atari import flag_capture_v0`

`agents= ["first_0", "second_0"]`

![flag_capture gif](atari_flag_capture.gif)

*AEC diagram*


A battle of memory and information.

A flag is hidden
on the map.
You can travel through the map and check
the squares in it. If it is the flag,
you score a point (and your opponent is penalized).
If it is a bomb, you get sent back to your starting location.
Otherwise, it will give you a hint to where the flag is,
either a direction or a distance.
Your player needs to be able to use information from both
your own search and your opponent's search in order to
narrow down the location of the flag quickly and effectively.


#### Environment parameters

Environment parameters are common to all Atari environments and are described in the [base Atari documentation](../atari.md) .

