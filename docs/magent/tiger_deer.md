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
import: "pettingzoo.magent import tiger_deer_v1"
agent-labels: "agents= [ deer_[0-100], tiger_[0-19] ]"
---

{% include info_box.md %}



In tiger-deer, there are a number of tigers who must team up to take down the deer (two tigers must attack a deer in the same step to receive reward). If they do not eat the deer, they will not survive. At the same time, the deer are trying to avoid getting attacked.  

Tiger action options: `[do_nothing, move_4, attack_4]`

Tiger's reward is given as:

* 1 reward for attacking a deer alongside another tiger

Deer action options: `[do_nothing, move_4]`

Deer's reward is given as:

* -1 reward for dying

Observation space: `[empty, obstacle, deer, tigers, binary_agent_id(10), one_hot_action, last_reward]`

Map size: 45x45

### Arguments

```
tiger_deer_v1.env(max_frames=500)
```



`max_frames`:  number of frames (a step for each agent) until game terminates
