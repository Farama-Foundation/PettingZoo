---
actions: "Discrete/Continuous"
title: "Simple Push"
agents: "2"
manual-control: "No"
action-shape: "(5)"
action-values: "Discrete(5)/Box(0.0, 1.0, (5,))"
observation-shape: "(8),(19)"
observation-values: "(-inf,inf)"
state-shape: "(27,)"
state-values: "(-inf,inf)"
import: "from pettingzoo.mpe import simple_push_v2"
agent-labels: "agents= [adversary_0, agent_0]"
---

<div class="docu-info" markdown="1">
{% include info_box.md %}
</div>

<div class="docu-content" markdown="1">
<div class="appear_big env-title" markdown="1">
{% include env_icon.md %}
## {{page.title}}
</div>




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