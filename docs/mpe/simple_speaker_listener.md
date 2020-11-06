---
actions: "Discrete"
title: "Simple Speaker Listener"
agents: "2"
manual-control: "No"
action-shape: "(3),(5)"
action-values: "Discrete(3),(5)"
observation-shape: "(3),(11)"
observation-values: "(-inf,inf)"
average-total-reward: "-80.9"
import: "from pettingzoo.mpe import simple_speaker_listener_v3"
agent-labels: "agents=[speaker_0, listener_0]"
---

{% include info_box.md %}



This environment is similar to simple_reference, except that one agent is the ‘speaker’ (gray) and can speak but cannot move, while the other agent is the listener (cannot speak, but must navigate to correct landmark).

Speaker observation space: `[goal_id]`

Listener observation space: `[self_vel, all_landmark_rel_positions, communication]`

Speaker action space: `[say_0, say_1, say_2, say_3, say_4, say_5, say_6, say_7, say_8, say_9]`

Listener action space: `[no_action, move_left, move_right, move_down, move_up]`

### Arguments

```
simple_speaker_listener.env(max_cycles=25)
```



`max_cycles`:  number of frames (a step for each agent) until game terminates
