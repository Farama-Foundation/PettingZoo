---
title: "Gather"
env_icon: "../../../_static/img/icons/MAgent/Gather.png"
---

# Gather

```{figure} magent_gather.gif 
:width: 140px
:name: gather
```

This environment is part of the <a href='..'>MAgent environments</a>. Please read that page first for general information.

| Import             | `from pettingzoo.magent import gather_v4` |
|--------------------|-------------------------------------------|
| Actions            | Discrete                                  |
| Parallel API       | Yes                                       |
| Manual Control     | No                                        |
| Agents             | `agents= [ omnivore_[0-494] ]`            |
| Agents             | 495                                       |
| Action Shape       | (33)                                      |
| Action Values      | Discrete(33)                              |
| Observation Shape  | (15,15,5)                                 |
| Observation Values | [0,2]                                     |
| State Shape        | (200, 200, 5)                             |
| State Values       | (0, 2)                                    |

```{figure} ../../_static/img/aec/magent_gather_aec.svg
:width: 200px
:name: gather
```

In gather, the agents gain reward by eating food. Food needs to be broken down by 5 "attacks" before it is absorbed. Since there is finite food on the map, there is competitive pressure between agents over the food. You expect to see that agents coordinate by not attacking each other until food is scarce. When food is scarce, agents may attack each other to try to monopolize the food. Agents can kill each other with a single attack.

### Arguments

``` python
gather_v4.env(minimap_mode=False, step_reward=-0.01, attack_penalty=-0.1,
dead_penalty=-1, attack_food_reward=0.5, max_cycles=500, extra_features=False)
```

`minimap_mode`: Turns on global minimap observations. These observations include your and your opponents piece densities binned over the 2d grid of the observation space. Also includes your `agent_position`, the absolute position on the map (rescaled from 0 to 1).

`step_reward`:  reward added unconditionally

`dead_penalty`:  reward added when killed

`attack_penalty`:  reward added for attacking

`attack_food_reward`:  Reward added for attacking a food

`max_cycles`:  number of frames (a step for each agent) until game terminates

`extra_features`: Adds additional features to observation (see table). Default False

#### Action Space

Key: `move_N` means N separate actions, one to move to each of the N nearest squares on the grid.

Action options: `[do_nothing, move_28, attack_4]`

#### Reward

Reward is given as:

* 5 reward for eating a food (requires multiple attacks)
* -0.01 reward every step (step_reward option)
* -0.1 reward for attacking (attack_penalty option)
* -1 reward for dying (dead_penalty option)
* 0.5 reward for attacking a food (attack_food_reward option)

#### Observation space

The observation space is a 15x15 map with the below channels (in order):

feature | number of channels
--- | ---
obstacle/off the map| 1
omnivore_presence| 1
omnivore_hp| 1
omnivore_minimap(minimap_mode=True)| 1
food_presense| 1
food_hp| 1
food_minimap(minimap_mode=True)| 1
one_hot_action(extra_features=True)| 33
last_reward(extra_features=True)| 1
agent_position(minimap_mode=True)| 2

### State space

The observation space is a 200x200 map. It contains the following channels, which are (in order):

feature | number of channels
--- | ---
obstacle map| 1
omnivore_presence| 1
omnivore_hp| 1
food_presence| 1
food_hp| 1
one_hot_action(extra_features=True)|  33 (max action space)
last_reward(extra_features=True)| 1



### Version History

* v4: Underlying library fix (1.18.0)
* v3: Fixed bugs and changed default parameters (1.7.0)
* v2: Observation space bound fix, bumped version of all environments due to adoption of new agent iteration scheme where all agents are iterated over after they are done (1.4.0)
* v1: Agent order under death changed (1.3.0)
* v0: Initial versions release (1.0.0)
