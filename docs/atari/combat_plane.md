---
layout: "docu"
title: "Combat: Plane"
actions: "Discrete"
agents: "2"
manual-control: "No"
action-shape: "(1,)"
action-values: "[0,17]"
observation-shape: "(256, 160, 3)"
observation-values: "(0,255)"
import: "from pettingzoo.atari import combat_jet_v1"
agent-labels: "agents= ['first_0', 'second_0']"
---

{% include info_box.md %}




*Combat*'s plane mode is an adversarial game where timing,
positioning, and keeping track of your opponent's complex
movements are key.

The players fly around the map, able to control flight direction
but not your speed.

When your opponent is hit by your bullet,
you score a point.

Whenever you score a point, you are rewarded +1 and your opponent is penalized -1.

[Official Combat manual](https://atariage.com/manual_html_page.php?SoftwareID=935)


#### Environment parameters

Some environment parameters are common to all Atari environments and are described in the [base Atari documentation](../atari).

Parameters specific to combat-plane are

```
combat_plane.env(game_version="jet", guided_missile=True)
```

`game_version`:  Accepted arguments are "jet" or "bi-plane". Whether the plane is a bi-plane or a jet. (Jets move faster)

`guided_missile`:  Whether the missile can be directed after being fired, or whether it is on a fixed path.
