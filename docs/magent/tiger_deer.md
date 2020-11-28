---
layout: "docu"
title: "Tiger-Deer"
actions: "Discrete"
agents: "121"
manual-control: "No"
action-shape: "(5),(9)"
action-values: "Discrete(5),(9)"
observation-shape: "(3,3,21), (9,9,25)"
observation-values: "[0,2]"
import: "pettingzoo.magent import tiger_deer_v3"
agent-labels: "agents= [ deer_[0-100], tiger_[0-19] ]"
---

{% include info_box.md %}



In tiger-deer, there are a number of tigers who are only rewarded for teaming up to take down the deer (two tigers must attack a deer in the same step to receive reward). If they do not eat the deer, they will slowly lose heath until they die. At the same time, the deer are trying to avoid getting attacked.  

Tiger action space: `[do_nothing, move_4, attack_4]`

Tiger's reward scheme is:

* 1 reward for attacking a deer alongside another tiger

Deer action space: `[do_nothing, move_4]`

Deer's reward scheme is:

* -1 reward for dying
* -0.1 for being attacked

Observation space: `[obstacle, my_team_presence, my_team_presence_health, other_team_presence, other_team_presence_health, one_hot_action, last_reward]`

### Arguments

```
tiger_deer_v3.env(map_size=45, minimap_mode=False, tiger_step_recover=-0.1, deer_attacked=-0.1, max_cycles=500)
```

`map_size`: Sets dimensions of the (square) map. Increasing the size increases the number of agents.

`minimap_mode`: Turns on global minimap observations. These observations include your and your opponents piece densities binned over the 2d grid of the observation space. Also includes your `agent_position`, the absolute position on the map (rescaled from 0 to 1).

`tiger_step_recover`: Amount of health a tiger gains/loses per turn (tigers have health 10 and get health 8 from killing a deer)

`deer_attacked`: Reward a deer gets for being attacked

`max_cycles`:  number of frames (a step for each agent) until game terminates
