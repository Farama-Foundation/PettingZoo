---
actions: "Discrete"
title: "Battle"
agents: "162"
manual-control: "No"
action-shape: "(21)"
action-values: "Discrete(21)"
observation-shape: "(13,13,41)"
observation-values: "[0,2]"
import: "pettingzoo.magent import battle_v1"
agent-labels: "agents= [red_[0-80], blue_[0-80]]"
---

{% include info_box.md %}



A large-scale team battle.

Like all MAgent environments, agents can either move or attack each turn. An attack against another agent on their own team will not be registered.

Action options: `[do_nothing, move_12, attack_8]`

Reward is given as:

* 5 reward for killing an opponent
* -0.005 reward every step (step_reward option)
* -0.1 reward for attacking (attack_penalty option)
* 0.2 reward for attacking an opponent (attack_opponent_reward option)
* -0.1 reward for dying (dead_penalty option)

If multiple options apply, rewards are added together.

Observation space: `[empty, obstacle, red, blue, minimap_red, minimap_blue, binary_agent_id(10), one_hot_action, last_reward, agent_position]`

Map size: 45x45

### Arguments

```
battle_v1.env(step_reward-0.005, dead_penalty=-0.1, attack_penalty=-0.1, attack_opponent_reward=0.2, max_frames=1000)
```



`step_reward`:  reward added unconditionally

`dead_penalty`:  reward added when killed

`attack_penalty`:  reward added for attacking

`attack_opponent_reward`:  Reward added for attacking an opponent

`max_frames`:  number of frames (a step for each agent) until game terminates
