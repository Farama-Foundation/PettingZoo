---
actions: "Discrete"
title: "Battlefield"
agents: "24"
manual-control: "No"
action-shape: "(21)"
action-values: "Discrete(21)"
observation-shape: "(13,13,41)"
observation-values: "[0,2]"
import: "pettingzoo.magent import battlefield_v2"
agent-labels: "agents= [red_[0-11], blue_[0-11]]"
---

{% include info_box.md %}



Same as [battle](./battle) but with fewer agents arrayed in a larger space with obstacles.

A small-scale team battle, where agents have to figure out the optimal way to coordinate their small team in a large space and maneuver around obstacles in order to defeat the opposing team. Agents are rewarded for their individual performance, and not for the performance of their neighbors, so coordination is difficult.  Agents slowly regain HP over time, so it is best to kill an opposing agent quickly. Specifically, agents have 10 HP, are damaged 2 HP by each attack, and recover 0.1 HP every turn.

Like all MAgent environments, agents can either move or attack each turn. An attack against another agent on their own team will not be registered.

#### Action Space

Key: `move_N` means N separate actions, one to move to each of the N nearest squares on the grid.

Action options: `[do_nothing, move_12, attack_8]`

#### Reward

Reward is given as:

* 5 reward for killing an opponent
* -0.005 reward every step (step_reward option)
* -0.1 reward for attacking (attack_penalty option)
* 0.2 reward for attacking an opponent (attack_opponent_reward option)
* -0.1 reward for dying (dead_penalty option)

If multiple options apply, rewards are added.

#### Observation space

The observation space is a 13x13 map with 41 channels, which are (in order):

name | number of channels
--- | ---
obstacle/off the map| 1
my_team_presence| 1
my_team_hp| 1
my_team_minimap| 1
other_team_presence| 1
other_team_hp| 1
other_team_minimap| 1
binary_agent_id| 10
one_hot_action| 21
last_reward| 1
agent_position| 2

### Arguments

```
battle_v2.env(map_size=80, minimap_mode=True, step_reward-0.005, dead_penalty=-0.1, attack_penalty=-0.1, attack_opponent_reward=0.2, max_cycles=1000)
```

`map_size`: Sets dimensions of the (square) map. Minimum size is 45.

`minimap_mode`: Turns on global minimap observations. These observations include your and your opponents piece densities binned over the 2d grid of the observation space. Also includes your `agent_position`, the absolute position on the map (rescaled from 0 to 1).

`step_reward`:  reward added unconditionally

`dead_penalty`:  reward added when killed

`attack_penalty`:  reward added for attacking

`attack_opponent_reward`:  Reward added for attacking an opponent

`max_cycles`:  number of frames (a step for each agent) until game terminates
