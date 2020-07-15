---
layout: "docu"
actions: "Discrete"
agents: "2"
manual-control: "No"
action-shape: "(1,)"
action-values: "[0,17]"
observation-shape: "(210, 160, 3)"
observation-values: "(0,255)"
average-total-reward: "-2.0"
---

### Entombed: Cooperative

This environment is part of the [Atari environments](../atari). Please read that page first for general information.

{% include table.md %}


`from pettingzoo.atari import entombed_cooperative_v0`

`agents= ["first_0", "second_0"]`

![entombed_cooperative gif](atari_entombed_cooperative.gif)

*AEC diagram*


Entomb's cooperative version is an exploration game
where you need to work with your teammate to make it
as far as possible into the maze.

You both need to quickly navigate down a constantly generating
maze you can only see part of. If you get stuck, you lose.
Note you can easily find yourself in a dead-end excapable only through the use of rare power-ups.
If players help each other by the use of these powerups, they can last longer.
In addition, there dangerous zombies lurking around to avoid.

The after a 5 second hiatus after starting or restarting due to dying, players get 1 reward every 5 seconds (1 second = 60 frames, 5 seconds = 300 frames). Note that this is similar, but not exactly equal to the single player version of entombed, so the rewards should not be compared directly.

[Official Entombed manual](https://atariage.com/manual_html_page.php?SoftwareLabelID=165)


#### Environment parameters

Environment parameters are common to all Atari environments and are described in the [base Atari documentation](../atari) .
