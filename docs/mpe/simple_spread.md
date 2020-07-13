---
layout: docu
observations: Vector
actions: Discrete
agents: 3
manual-control: No
action-shape: (5)
action-values: Discrete(5)
observation-shape: (18)
observation-values: (-inf,inf)
num-states: ?
---

### Simple Spread

This environment is part of the [MPE environments](../mpe). Please read that page first for general information.


`pettingzoo.mpe import simple_spread_v0`

`agents= [agent_0, agent_1, agent_2]`

![](mpe_simple_spread.gif)

*AEC diagram*

This environment has N agents, N landmarks (default N=3). At a high level, agents must learn to cover all the landmarks while avoiding collisions.

More specifically, all agents are globally rewarded based on how far the closest agent is to each landmark (sum of the minimum distances). Locally, the agents are penalized if they collide with other agents (-1 for each collision). The relative weights of these rewards can be controlled with the `local_ratio` parameter.

Agent observations: `[self_vel, self_pos, landmark_rel_positions, other_agent_rel_positions, communication]`

Agent action space: `[no_action, move_left, move_right, move_down, move_up]`

```
simple_spread.env(seed=None, N=3, local_ratio=0.5, max_frames=100)
```

```
seed: seed for random values. Set to None to use machine random source. Set to fixed value for deterministic behavior

N: number of agents and landmarks

local_ratio: Weight applied to local reward and global reward. Global reward weight will always be 1 - local reward weight.

max_frames: number of frames (a step for each agent) until game terminates
```
