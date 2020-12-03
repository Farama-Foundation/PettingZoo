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


In tiger-deer, there are a number of tigers who are only rewarded for teaming up to take down the deer (two tigers must attack a deer in the same step to receive reward). If they do not eat the deer, they will slowly lose 0.1 HP each turn until they die. If they do eat the deer they regain 8 health (they have 10 health to start). At the same time, the deer are trying to avoid getting attacked. Deer start with 5 HP, lose 1 HP when attacked, and regain 0.1 HP each turn. Deer should run from tigers and tigers should form small teams to take down deer.


#### Action Space

Key: `move_N` means N separate actions, one to move to each of the N nearest squares on the grid.

Tiger action space: `[do_nothing, move_4, attack_4]`

Deer action space: `[do_nothing, move_4]`

#### Reward

Tiger's reward scheme is:

* 1 reward for attacking a deer alongside another tiger

Deer's reward scheme is:

* -1 reward for dying
* -0.1 for being attacked

#### Observation space

The observation space is a 3x3 map with 21 channels for deer and 9x9 map with 25 channels for tigers, which are (in order):

name | number of channels
--- | ---
obstacle/off the map| 1
my_team_presence| 1
my_team_hp| 1
other_team_presence| 1
other_team_hp| 1
binary_agent_id| 10
one_hot_action| 5 Deer/9 Tiger
last_reward| 1
agent_position| 2

### Arguments

```
tiger_deer_v3.env(map_size=45, minimap_mode=False, tiger_step_recover=-0.1, deer_attacked=-0.1, max_cycles=500)
```

`map_size`: Sets dimensions of the (square) map. Increasing the size increases the number of agents.  Minimum size is 10.

`minimap_mode`: Turns on global minimap observations. These observations include your and your opponents piece densities binned over the 2d grid of the observation space. Also includes your `agent_position`, the absolute position on the map (rescaled from 0 to 1).

`tiger_step_recover`: Amount of health a tiger gains/loses per turn (tigers have health 10 and get health 8 from killing a deer)

`deer_attacked`: Reward a deer gets for being attacked

`max_cycles`:  number of frames (a step for each agent) until game terminates
