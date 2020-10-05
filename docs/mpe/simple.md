---
actions: "Discrete"
title: "Simple"
agents: "1"
manual-control: "No"
action-shape: "(5)"
action-values: "Discrete(5)"
observation-shape: "(4)"
observation-values: "(-inf,inf)"
import: "from pettingzoo.mpe import simple_v1"
agent-labels: "agents= [agent_0]"
---

{% include info_box.md %}



In this environment a single agent sees a landmark position and is rewarded based on how close it gets to the landmark (Euclidian distance). This is not a multiagent environment, and is primarily intended for debugging purposes.

Observation space: `[self_vel, landmark_rel_position]`

### Arguments

```
simple.env(max_frames=25)
```



`max_frames`:  number of frames (a step for each agent) until game terminates

