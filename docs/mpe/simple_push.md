---
actions: "Discrete"
title: "Simple Push"
agents: "2"
manual-control: "No"
action-shape: "(5)"
action-values: "Discrete(5)"
observation-shape: "(8),(19)"
observation-values: "(-inf,inf)"
import: "from pettingzoo.mpe import simple_push_v2"
agent-labels: "agents= [adversary_0, agent_0]"
---

{% include info_box.md %}



This environment has 1 good agent, 1 adversary, and 1 landmark. The good agent is rewarded based on the distance to the landmark. The adversary is rewarded if it is close to the landmark, and if the agent is far from the landmark (the difference of the distances). Thus the adversary must learn to push the good agent away from the landmark.

Agent observation space: `[self_vel, goal_rel_position, goal_landmark_id, all_landmark_rel_positions, landmark_ids, other_agent_rel_positions]`

Adversary observation space: `[self_vel, all_landmark_rel_positions, other_agent_rel_positions]`

Agent action space: `[no_action, move_left, move_right, move_down, move_up]`

Adversary action space: `[no_action, move_left, move_right, move_down, move_up]`

### Arguments

```
simple_push.env(max_cycles=25)
```



`max_cycles`:  number of frames (a step for each agent) until game terminates

