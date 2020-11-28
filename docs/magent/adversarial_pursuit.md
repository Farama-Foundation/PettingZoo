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

In this environment, red agents work navigate the obstacles and attack the blue agents, who in turn work to avoid attatcks. To be effect the red agents, who are much are slower and larger than the blue agents, must work together to trap blue agents and attack them continually.

Predator action options: `[do_nothing, move_4, attack_8]`

Predator's reward is given as:

* 1 reward for attacking a prey
* -0.2 reward for attacking (attack_penalty option)

Prey action options: `[do_nothing, move_8]`

Prey's reward is given as:

* -1 reward for being attacked

Observation space: `[obstacle, my_team_presence, my_team_presence_health, other_team_presence, other_team_presence_health, one_hot_action, last_reward]`

### Arguments

```
adversarial_pursuit_v2.env(map_size=45, minimap_mode=False, attack_penalty=-0.2, max_cycles=500)
```

`map_size`: Sets dimensions of the (square) map. Increasing the size increases the number of agents.

`minimap_mode`: Turns on global minimap observations. These observations include your and your opponents piece densities binned over the 2d grid of the observation space. Also includes your `agent_position`, the absolute position on the map (rescaled from 0 to 1).

`attack_penalty`:  Adds the following value to the reward whenever an attacking action is taken

`max_cycles`:  number of frames (a step for each agent) until game terminates
