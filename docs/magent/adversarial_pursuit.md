---
actions: "Discrete"
title: "Adversarial Pursuit"
agents: "75"
manual-control: "No"
action-shape: "(9),(13)"
action-values: "Discrete(9),(13)"
observation-shape: "(9,9,15), (10,10,19)"
observation-values: "[0,2]"
import: "pettingzoo.magent import adversarial_pursuit_v2"
agent-labels: "agents= [predator_[0-24], prey_[0-49]]"
---

{% include info_box.md %}

The red agents must navigate the obstacles and tag (similar to attacking, but without damaging) the blue agents. The blue agents should try to avoid being tagged. To be effective, the red agents, who are much are slower and larger than the blue agents, must work together to trap blue agents so they can be tagged continually.

#### Action Space

Key: `move_N` means N separate actions, one to move to each of the N nearest squares on the grid.

Predator action options: `[do_nothing, move_4, tag_8]`

#### Reward

Predator's reward is given as:

* 1 reward for tagging a prey
* -0.2 reward for tagging anywhere (`tag_penalty` option)

Prey action options: `[do_nothing, move_8]`

Prey's reward is given as:

* -1 reward for being tagged

Observation space: `[obstacle, my_team_presence, my_team_presence_health, other_team_presence, other_team_presence_health, one_hot_action, last_reward]`

### Arguments

```
adversarial_pursuit_v2.env(map_size=45, minimap_mode=False, tag_penalty=-0.2, max_cycles=500)
```

`map_size`: Sets dimensions of the (square) map. Increasing the size increases the number of agents. Minimum size is 7.

`minimap_mode`: Turns on global minimap observations. These observations include your and your opponents piece densities binned over the 2d grid of the observation space. Also includes your `agent_position`, the absolute position on the map (rescaled from 0 to 1).

`tag_penalty`:  reward when red agents tag anything

`max_cycles`:  number of frames (a step for each agent) until game terminates
