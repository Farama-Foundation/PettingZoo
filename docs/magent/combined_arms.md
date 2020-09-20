---
actions: "Discrete"
title: "Combined Arms"
agents: "162"
manual-control: "No"
action-shape: "(9),(25)"
action-values: "Discrete(9),(25)"
observation-shape: "(13,13,35), (13,13,51)"
observation-values: "[0,2]"
import: "pettingzoo.magent import combined_arms_v1"
agent-labels: "agents= [redmelee_[0-44], redranged_[0-35], bluemelee_[0-44], blueranged_[0-35]]"
---

{% include info_box.md %}



A large-scale team battle. Here there are two types of agents on each team, ranged units which can attack father and move faster but have less HP, and melee units which can only attack close units and move more slowly but have more HP. Unlike battle and battlefield, agents can attack units on their own team (they just are not rewarded for doing so).

Melee action options: `[do_nothing, move_4, attack_4]`

Ranged action options: `[do_nothing, move_12, attack_12]`

Reward is given as:

* 100 reward for killing an opponent
* -0.01 reward every step (step_reward option)
* -0.1 reward for attacking (attack_penalty option)
* 2 reward for attacking an opponent (attack_opponent_reward option)
* -1 reward for dying (dead_penalty option)


If multiple options apply, rewards are added together

Observation space: `[empty, obstacle, agent_maps, agent_minimaps, binary_agent_id(10), one_hot_action, last_reward, agent_position]`

Map size: 45x45

### Arguments

```
combined_arms_v1.env(step_reward-0.01, dead_penalty=-0.1, attack_penalty=-1, attack_opponent_reward=2, max_frames=1000)
```



`step_reward`:  reward added unconditionally

`dead_penalty`:  reward added when killed

`attack_penalty`:  reward added for attacking

`attack_opponent_reward`:  Reward added for attacking an opponent

`max_frames`:  number of frames (a step for each agent) until game terminates
