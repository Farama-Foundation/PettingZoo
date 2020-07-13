---
layout: "docu"
observations: "Vector"
actions: "Discrete"
agents: "2"
manual-control: "No"
action-shape: "(3),(5)"
action-values: "Discrete(3),(5)"
observation-shape: "(3),(11)"
observation-values: "(-inf,inf)"
num-states: "?"
---

### Simple Speaker Listener

This environment is part of the [MPE environments](../mpe). Please read that page first for general information.

{% include table.md %}


`pettingzoo.mpe import simple_speaker_listener_v0`

`agents=[speaker_0, listener_0]`

![](mpe_simple_speaker_listen.gif)

*AEC diagram*

This environment is similar to simple_reference, except that one agent is the ‘speaker’ (gray) and can speak but cannot move, while the other agent is the listener (cannot speak, but must navigate to correct landmark).

Speaker observation space: `[goal_id]`

Listener observation space: `[self_vel, all_landmark_rel_positions, communication]`

Speaker action space: `[say_0, say_1, say_2, say_3, say_4, say_5, say_6, say_7, say_8, say_9]`

Listener action space: `[no_action, move_left, move_right, move_down, move_up]`

```
simple_speaker_listener.env(seed=None, max_frames=100)
```

```
seed: seed for random values. Set to None to use machine random source. Set to fixed value for deterministic behavior

max_frames: number of frames (a step for each agent) until game terminates
```
