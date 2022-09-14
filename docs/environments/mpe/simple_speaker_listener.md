---
env_icon: "../../../_static/img/icons/mpe/simple_speaker_listener.png"
---

# Simple Speaker Listener

```{figure} mpe_simple_speaker_listener.gif 
:width: 140px
:name: simple_speaker_listener
```

This environment is part of the <a href='..'>MPE environments</a>. Please read that page first for general information.

| Import               | `from pettingzoo.mpe import simple_speaker_listener_v3` |
|----------------------|---------------------------------------------------------|
| Actions              | Discrete/Continuous                                     |
| Parallel API         | Yes                                                     |
| Manual Control       | No                                                      |
| Agents               | `agents=[speaker_0, listener_0]`                        |
| Agents               | 2                                                       |
| Action Shape         | (3),(5)                                                 |
| Action Values        | Discrete(3),(5)/Box(0.0, 1.0, (3)), Box(0.0, 1.0, (5))  |
| Observation Shape    | (3),(11)                                                |
| Observation Values   | (-inf,inf)                                              |
| State Shape          | (14,)                                                   |
| State Values         | (-inf,inf)                                              |
| Average Total Reward | -80.9                                                   |

```{figure} ../../_static/img/aec/mpe_simple_speaker_listener_aec.svg
:width: 200px
:name: simple_speaker_listener
```

This environment is similar to simple_reference, except that one agent is the 'speaker' (gray) and can speak but cannot move, while the other agent is the listener (cannot speak, but must navigate to correct landmark).

Speaker observation space: `[goal_id]`

Listener observation space: `[self_vel, all_landmark_rel_positions, communication]`

Speaker action space: `[say_0, say_1, say_2, say_3, say_4, say_5, say_6, say_7, say_8, say_9]`

Listener action space: `[no_action, move_left, move_right, move_down, move_up]`

### Arguments

``` python
simple_speaker_listener_v2.env(max_cycles=25, continuous_actions=False)
```



`max_cycles`:  number of frames (a step for each agent) until game terminates

`continuous_actions`: Whether agent action spaces are discrete(default) or continuous

