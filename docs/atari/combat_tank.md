---
layout: "docu"
title: "Combat: Tank"
actions: "Discrete"
agents: "2"
manual-control: "No"
action-shape: "(1,)"
action-values: "[0,17]"
observation-shape: "(256, 160, 3)"
observation-values: "(0,255)"
import: "from pettingzoo.atari import combat_tank_v1"
agent-labels: "agents= ['first_0', 'second_0']"
---

{% include info_box.md %}



*Combat*'s classic tank mode is an adversarial game where prediction, and positioning are key.

The players move around the map. When your opponent is hit by your bullet,
you score a point. Note that your opponent gets blasted through obstacles when it is hit, potentially putting it in a good position to hit you back.

Whenever you score a point, you are rewarded +1 and your opponent is penalized -1.

[Official Combat manual](https://atariage.com/manual_html_page.php?SoftwareID=935)


#### Environment parameters

Some environment parameters are common to all Atari environments and are described in the [base Atari documentation](../atari).

Parameters specific to combat-tank are

```
combat_tank.env(has_maze=False, is_invisible=False, billiard_hit=False)
```

`has_maze`:  Set to true to have the map be a maze instead of an open field

`is_invisible`:  If true, tanks are invisible unless they are firing or are running into a wall.

`billiard_hit`:  If true, bullets bounce off walls, in fact, like billiards, they only count if they hit the opponent's tank after bouncing off a wall.
