---
actions: "Discrete"
title: "Gather"
agents: "495"
manual-control: "No"
action-shape: "(33)"
action-values: "Discrete(33)"
observation-shape: "(15,15,43)"
observation-values: "[0,2]"
import: "pettingzoo.magent import gather_v1"
agent-labels: "agents= [ omnivore_[0-494] ]"
---

{% include info_box.md %}



In gather, the agents must gain reward by eating food or fighting each other. Agent's don't die unless attacked. You expect to see that agents coordinate by not attacking each other until food is scarce.

Action options: `[do_nothing, move_28, attack_4]`

Reward is given as:

* 1 reward for attacking an agent
* 5 reward for eating a food (requires multiple attacks)
* -0.01 reward every step (step_reward option)
* -0.1 reward for attacking (attack_penalty option)
* -1 reward for dying (dead_penalty option)
* 0.5 reward for attacking a food (attack_food_reward option)

Observation space: `[empty, obstacle, omnivore, food, omnivore_minimap, food_minimap, one_hot_action, last_reward, agent_position]`

Map size: 200x200

### Arguments

```
gather_v1.env(step_reward=-0.01, attack_penalty=-0.1, dead_penalty=-1, attack_food_reward=0.5, max_frames=500)
```



`step_reward`:  reward added unconditionally

`dead_penalty`:  reward added when killed

`attack_penalty`:  reward added for attacking

`attack_food_reward`:  Reward added for attacking a food

`max_frames`:  number of frames (a step for each agent) until game terminates
