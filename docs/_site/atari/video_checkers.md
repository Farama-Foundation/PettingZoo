
### Video Checkers

This environment is part of the [Atari environments](../atari.md). Please read that page first for general information.

| Observations | Actions | Agents  | Manual Control | Action Shape | Action Values | Observation Shape | Observation Values | Num States |
|--------------|---------|---------|----------------|--------------|---------------|-------------------|--------------------|------------|
| Graphical    | Discrete  | 2 | No      | (1,)    | [0,17]         | (210, 160, 3)         | (0,255)            | ?          |

`from pettingzoo.atari import video_checkers_v0`

`agents= ["first_0", "second_0"]`

![video_checkers gif](atari_video_checkers.gif)

*AEC diagram*

A classical strategy game with arcade style controls.

Capture all of your opponents pieces by jumping over them. To move a piece, you must select a piece by hovering the cursor and pressing fire (action 1), moving the cursor, and pressing fire again. Note that the buttons must be held for multiple frames to be registered.

If you win by capturing all your opponent's pieces, you are rewarded +1 and your opponent -1.

Note that this is an extremely difficult game to learn, due to the extremely sparse reward, and the fact that doing nothing is a good strategy to never lose. 

#### Environment parameters

Environment parameters are common to all Atari environments and are described in the [base Atari documentation](../atari.md) .
