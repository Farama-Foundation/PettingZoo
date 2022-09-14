---
env_icon: "../../../_static/img/icons/mpe/simple_reference.png"
---

# Simple Reference

```{figure} mpe_simple_reference.gif 
:width: 140px
:name: simple_reference
```

This environment is part of the <a href='..'>MPE environments</a>. Please read that page first for general information.

| Import             | `from pettingzoo.mpe import simple_reference_v2` |
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

```{figure} ../../_static/img/aec/mpe_simple_reference_aec.svg
:width: 200px
:name: simple_reference
```

This environment has 2 agents and 3 landmarks of different colors. Each agent wants to get closer to their target landmark, which is known only by the other agents. Both agents are simultaneous speakers and listeners.

Locally, the agents are rewarded by their distance to their target landmark. Globally, all agents are rewarded by the average distance of all the agents to their respective landmarks. The relative weight of these rewards is controlled by the `local_ratio` parameter.

Agent observation space: `[self_vel, all_landmark_rel_positions, landmark_ids, goal_id, communication]`

Agent discrete action space: `[say_0, say_1, say_2, say_3, say_4, say_5, say_6, say_7, say_8, say_9] X [no_action, move_left, move_right, move_down, move_up]`

Where X is the Cartesian product (giving a total action space of 50).

Agent continuous action space: `[no_action, move_left, move_right, move_down, move_up, say_0, say_1, say_2, say_3, say_4, say_5, say_6, say_7, say_8, say_9]`

### Arguments


``` python
simple_reference_v2.env(local_ratio=0.5, max_cycles=25, continuous_actions=False)
```



`local_ratio`:  Weight applied to local reward and global reward. Global reward weight will always be 1 - local reward weight.

`max_cycles`:  number of frames (a step for each agent) until game terminates

`continuous_actions`: Whether agent action spaces are discrete(default) or continuous

