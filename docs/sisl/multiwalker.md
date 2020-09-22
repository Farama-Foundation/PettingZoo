---
actions: "Continuous"
title: "Multiwalker"
agents: "3"
manual-control: "No"
action-shape: "(4,)"
action-values: "(-1, 1)"
observation-shape: "(31,)"
observation-values: "[-5.333,5.333]"
average-total-reward: "-109.7"
import: "from pettingzoo.sisl import multiwalker_v3"
agent-labels: "agents= ['walker_0', 'walker_1', 'walker_2']"
---

{% include info_box.md %}



A package is placed on top of (by default) 3 pairs of robot legs which you control. The robots must learn to move the package as far as possible to the right. A positive reward is awarded to each walker, which is the change in the package distance summed with 130 times the change in the walker's position. A walker is given a reward of -100 if they fall and all walkers receive a reward of -100 if the package falls. By default, the environment is done if any walker or the package falls. If the `terminate_on_fall` setting is set to false, the game continues until the package falls. If the global reward mechanic is chosen, the mean of all rewards is given to each agent. Each walker exerts force on two joints in their two legs, giving a continuous action space represented as a 4 element vector. Each walker observes via a 31 element vector containing simulated noisy lidar data about the environment and information about neighboring walkers. The environment's duration is capped at 500 frames by default (can be controlled by the `max_frames` setting)

### Arguments

```
multiwalker.env(n_walkers=3, position_noise=1e-3, angle_noise=1e-3, reward_mech='local',
forward_reward=1.0, fall_reward=-100.0, drop_reward=-100.0, terminate_on_fall=True,
max_frames=500)
```



`n_walkers`:  number of bipedal walker agents in environment

`position_noise`:  noise applied to agent positional sensor observations

`angle_noise`:  noise applied to agent rotational sensor observations

`local_ratio`: Proportion of reward allocated locally vs distributed among all agents

`forward_reward`:  reward applied for an agent standing, scaled by agent's x coordinate

`fall_reward`:  reward applied when an agent falls down

`drop_reward`:  reward applied for each fallen walker in environment

`terminate_on_fall`:  toggles whether agent is done if it falls down

`max_frames`:  after max_frames steps all agents will return done
