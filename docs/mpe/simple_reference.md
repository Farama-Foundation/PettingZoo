---
actions: "Discrete"
title: "Simple Reference"
agents: "2"
manual-control: "No"
action-shape: "(50)"
action-values: "Discrete(50)"
observation-shape: "(21)"
observation-values: "(-inf,inf)"
average-total-reward: "-57.1"
import: "from pettingzoo.mpe import simple_reference_v2"
agent-labels: "agents= [agent_0, agent_1]"
---

{% include info_box.md %}



This environment has 2 agents and 3 landmarks of different colors. Each agent wants to get closer to their target landmark, which is known only by the other agents. Both agents are simultaneous speakers and listeners.

Locally, the agents are rewarded by their distance to their target landmark. Globally, all agents are rewarded by the average distance of all the agents to their respective landmarks. The relative weight of these rewards is controlled by the `local_ratio` parameter.

Agent observation space: `[self_vel, all_landmark_rel_positions, landmark_ids, goal_id, communication]`

Agent action space: `[say_0, say_1, say_2, say_3, say_4, say_5, say_6, say_7, say_8, say_9] X [no_action, move_left, move_right, move_down, move_up]`

Where X is the Cartesian product (giving a total action space of 50).

### Arguments


```
simple_reference.env(local_ratio=0.5, max_cycles=25)
```



`local_ratio`:  Weight applied to local reward and global reward. Global reward weight will always be 1 - local reward weight.

`max_cycles`:  number of frames (a step for each agent) until game terminates
