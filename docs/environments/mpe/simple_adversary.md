---
title: "Simple Adversary"
env_icon: "/_static/img/icons/MPE/SimpleAdversary.png"
---

# Simple Adversary

```{figure} mpe_simple_adversary.gif 
:width: 140px
:name: simple_adversary
```

This environment is part of the <a href='..'>MPE environments</a>. Please read that page first for general information.

| Import             | `from pettingzoo.mpe import simple_adversary_v2` |
|--------------------|--------------------------------------------------|
| Actions            | Discrete/Continuous                              |
| Parallel API       | Yes                                              |
| Manual Control     | No                                               |
| Agents             | `agents= [adversary_0, agent_0,agent_1]`         |
| Agents             | 3                                                |
| Action Shape       | (5)                                              |
| Action Values      | Discrete(5)/Box(0.0, 1.0, (5))                   |
| Observation Shape  | (8),(10)                                         |
| Observation Values | (-inf,inf)                                       |
| State Shape        | (28,)                                            |
| State Values       | (-inf,inf)                                       |

```{figure} ../../_static/img/aec/mpe_simple_adversary_aec.svg
:width: 200px
:name: simple_adversary
```

In this environment, there is 1 adversary (red), N good agents (green), N landmarks (default N=2). All agents observe the position of landmarks and other agents. One landmark is the ‘target landmark’ (colored green). Good agents are rewarded based on how close the closest one of them is to the target landmark, but negatively rewarded based on how close the adversary is to the target landmark. The adversary is rewarded based on distance to the target, but it doesn’t know which landmark is the target landmark. All rewards are unscaled Euclidean distance (see main MPE documentation for average distance). This means good agents have to learn to ‘split up’ and cover all landmarks to deceive the adversary.

Agent observation space: `[self_pos, self_vel, goal_rel_position, landmark_rel_position, other_agent_rel_positions]`

Adversary observation space: `[landmark_rel_position, other_agents_rel_positions]`

Agent action space: `[no_action, move_left, move_right, move_down, move_up]`

Adversary action space: `[no_action, move_left, move_right, move_down, move_up]`

### Arguments

``` python
simple_adversary_v2.env(N=2, max_cycles=25, continuous_actions=False)
```



`N`:  number of good agents and landmarks

`max_cycles`:  number of frames (a step for each agent) until game terminates

`continuous_actions`: Whether agent action spaces are discrete(default) or continuous
