---
title: "Simple"
env_icon: "../../../_static/img/icons/MPE/Simple.png"
---

# Simple

```{figure} mpe_simple.gif 
:width: 140px
:name: simple
```

This environment is part of the <a href='..'>MPE environments</a>. Please read that page first for general information.

| Import             | `from pettingzoo.mpe import simple_v2` |
|--------------------|----------------------------------------|
| Actions            | Discrete/Continuous                    |
| Parallel API       | Yes                                    |
| Manual Control     | No                                     |
| Agents             | `agents= [agent_0]`                    |
| Agents             | 1                                      |
| Action Shape       | (5)                                    |
| Action Values      | Discrete(5)/Box(0.0, 1.0, (5,))        |
| Observation Shape  | (4)                                    |
| Observation Values | (-inf,inf)                             |
| State Shape        | (4,)                                   |
| State Values       | (-inf,inf)                             |

```{figure} ../../_static/img/aec/mpe_simple_aec.svg
:width: 200px
:name: simple
```

In this environment a single agent sees a landmark position and is rewarded based on how close it gets to the landmark (Euclidean distance). This is not a multiagent environment, and is primarily intended for debugging purposes.

Observation space: `[self_vel, landmark_rel_position]`

### Arguments

``` python
simple_v2.env(max_cycles=25, continuous_actions=False)
```



`max_cycles`:  number of frames (a step for each agent) until game terminates

`continuous_actions`: Whether agent action spaces are discrete(default) or continuous
