---
actions: "Discrete"
title: "Simple"
agents: "1"
manual-control: "No"
action-shape: "(5)"
action-values: "Discrete(5)"
observation-shape: "(4)"
observation-values: "(-inf,inf)"
---

### Simple

This environment is part of the [MPE environments](../mpe). Please read that page first for general information.

{% include table.md %}


`pettingzoo.mpe.simple_v0`

`agents= [agent_0]`

![](mpe_simple.gif)

*AEC diagram*

In this environment a single agent sees a landmark position and is rewarded based on how close it gets to the landmark (Euclidian distance). This is not a multiagent environment, and is primarily intended for debugging purposes.

Observation space: `[self_vel, landmark_rel_position]`

```
simple.env(seed=None, max_frames=100)
```

```
seed: seed for random values. Set to None to use machine random source. Set to fixed value for deterministic behavior

max_frames: number of frames (a step for each agent) until game terminates
```
