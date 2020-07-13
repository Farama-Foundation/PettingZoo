---
layout: docu
actions: Discrete
agents: 2
manual-control: No
action-shape: (1,)
action-values: [0,17]
observation-shape: (210, 160, 3)
observation-values: (0,255)
---

### Surround: Original

This environment is part of the [Atari environments](../atari). Please read that page first for general information.


`from pettingzoo.atari import surround_v0`

`agents= ["first_0", "second_0"]`

![surround gif](atari_surround.gif)

*AEC diagram*

A competitive game of planning and strategy.

In surround, your goal is to avoid the walls. If you run into a wall, you are rewarded -1 points, and your opponent, +1 points.

But both players leave a trail of walls behind you, slowly filling the screen with obstacles. To avoid the obstacles as long as possible, you must plan your path to conserve space. Once that is mastered, a higher level aspect of the game comes into play, where both players literally try to surround the other with walls, so their opponent will run out of room and be forced to run into a wall.

[Official surround manual](https://atariage.com/manual_html_page.php?SoftwareLabelID=943)

#### Environment parameters

Environment parameters are common to all Atari environments and are described in the [base Atari documentation](../atari) .
