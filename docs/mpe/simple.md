
### Simple

This environment is part of the [MPE environments](../mpe.md). Please read that page first for general information.

| Observations | Actions  | Agents | Manual Control | Action Shape    | Action Values           | Observation Shape        | Observation Values | Num States |
|--------------|----------|--------|----------------|-----------------|-------------------------|--------------------------|--------------------|------------|
| Vector       | Discrete | 1      | No             | (5)             | Discrete(5)             | (4)                      | (-inf,inf)         | ?          |

`pettingzoo.mpe.simple_v0`

`agents= [agent_0]`

![](mpe_simple.gif)

*AEC diagram*

In this environment, a single agent sees landmark position, and is rewarded based on how close it gets to landmark (Euclidian distance). This is not a multiagent environment, and is primarily intended for debugging purposes.

Observation space: `[self_vel, landmark_rel_position]`

```
simple.env(seed=None, max_frames=100)
```

```
seed: seed for random values. Set to None to use machine random source. Set to fixed value for deterministic behavior

max_frames: number of frames (a step for each agent) until game terminates
```
