---
title: "Simple World Comm"
env_icon: "../../../_static/img/icons/MPE/SimpleWorldComm.png"
---

# Simple World Comm

```{figure} mpe_simple_world_comm.gif 
:width: 140px
:name: simple_world_comm
```

This environment is part of the <a href='..'>MPE environments</a>. Please read that page first for general information.

| Import             | `from pettingzoo.mpe import simple_world_comm_v2`                                   |
|--------------------|-------------------------------------------------------------------------------------|
| Actions            | Discrete/Continuous                                                                 |
| Parallel API       | Yes                                                                                 |
| Manual Control     | No                                                                                  |
| Agents             | `agents=[leadadversary_0, adversary_0, adversary_1, adversary_3, agent_0, agent_1]` |
| Agents             | 6                                                                                   |
| Action Shape       | (5),(20)                                                                            |
| Action Values      | Discrete(5),(20)/Box(0.0, 1.0, (5)), Box(0.0, 1.0, (9))                             |
| Observation Shape  | (28),(34)                                                                           |
| Observation Values | (-inf,inf)                                                                          |
| State Shape        | (192,)                                                                              |
| State Values       | (-inf,inf)                                                                          |

```{figure} ../../_static/img/aec/mpe_simple_world_comm_aec.svg
:width: 200px
:name: simple_world_comm
```

This environment is similar to simple_tag, except there is food (small blue balls) that the good agents are rewarded for being near, there are 'forests' that hide agents inside from being seen, and there is a ‘leader adversary' that can see the agents at all times and can communicate with the other adversaries to help coordinate the chase. By default, there are 2 good agents, 3 adversaries, 1 obstacles, 2 foods, and 2 forests.

In particular, the good agents reward, is -5 for every collision with an adversary, -2 x bound by the `bound` function described in simple_tag, +2 for every collision with a food, and -0.05 x minimum distance to any food. The adversarial agents are rewarded +5 for collisions and -0.1 x minimum distance to a good agent. s

Good agent observations: `[self_vel, self_pos, landmark_rel_positions, other_agent_rel_positions, other_agent_velocities, self_in_forest]`

Normal adversary observations:`[self_vel, self_pos, landmark_rel_positions, other_agent_rel_positions, other_agent_velocities, self_in_forest, leader_comm]`

Adversary leader observations: `[self_vel, self_pos, landmark_rel_positions, other_agent_rel_positions, other_agent_velocities, leader_comm]`

*Note that when the forests prevent an agent from being seen, the observation of that agents relative position is set to (0,0).*

Good agent action space: `[no_action, move_left, move_right, move_down, move_up]`

Normal adversary action space: `[no_action, move_left, move_right, move_down, move_up]`

Adversary leader discrete action space: `[say_0, say_1, say_2, say_3] X [no_action, move_left, move_right, move_down, move_up]`

Where X is the Cartesian product (giving a total action space of 50).

Adversary leader continuous action space: `[no_action, move_left, move_right, move_down, move_up, say_0, say_1, say_2, say_3]`

### Arguments

``` python
simple_world_comm.env(num_good=2, num_adversaries=4, num_obstacles=1,
                num_food=2, max_cycles=25, num_forests=2, continuous_actions=False)
```



`num_good`:  number of good agents

`num_adversaries`:  number of adversaries

`num_obstacles`:  number of obstacles

`num_food`:  number of food locations that good agents are rewarded at

`max_cycles`:  number of frames (a step for each agent) until game terminates

`num_forests`: number of forests that can hide agents inside from being seen

`continuous_actions`: Whether agent action spaces are discrete(default) or continuous
