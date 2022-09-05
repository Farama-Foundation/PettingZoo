---
actions: "Discrete/Continuous"
title: "Simple Push"
---

# Simple Push

```{figure} mpe_simple_push.gif 
:width: 140px
:name: simple_push
```

This environment is part of the <a href='..'>MPE environments</a>. Please read that page first for general information.

| Import             | `from pettingzoo.mpe import simple_push_v2` |
|--------------------|---------------------------------------------|
| Actions            | Discrete/Continuous                         |
| Parallel API       | Yes                                         |
| Manual Control     | No                                          |
| Agents             | `agents= [adversary_0, agent_0]`            |
| Agents             | 2                                           |
| Action Shape       | (5)                                         |
| Action Values      | Discrete(5)/Box(0.0, 1.0, (5,))             |
| Observation Shape  | (8),(19)                                    |
| Observation Values | (-inf,inf)                                  |
| State Shape        | (27,)                                       |
| State Values       | (-inf,inf)                                  |

```{figure} ../../_static/img/aec/mpe_simple_push_aec.svg
:width: 200px
:name: simple_push
```

This environment has 1 good agent, 1 adversary, and 1 landmark. The good agent is rewarded based on the distance to the landmark. The adversary is rewarded if it is close to the landmark, and if the agent is far from the landmark (the difference of the distances). Thus the adversary must learn to push the good agent away from the landmark.

Agent observation space: `[self_vel, goal_rel_position, goal_landmark_id, all_landmark_rel_positions, landmark_ids, other_agent_rel_positions]`

Adversary observation space: `[self_vel, all_landmark_rel_positions, other_agent_rel_positions]`

Agent action space: `[no_action, move_left, move_right, move_down, move_up]`

Adversary action space: `[no_action, move_left, move_right, move_down, move_up]`

### Arguments

``` python
simple_push_v2.env(max_cycles=25, continuous_actions=False)
```



`max_cycles`:  number of frames (a step for each agent) until game terminates

</div>