---
actions: "Discrete/Continuous"
title: "Simple Spread"
agents: "3"
manual-control: "No"
action-shape: "(5)"
action-values: "Discrete(5)/Box(0.0, 1.0, (5))"
observation-shape: "(18)"
observation-values: "(-inf,inf)"
state-shape: "(54,)"
state-values: "(-inf,inf)"
average-total-reward: "-115.6"
import: "from pettingzoo.mpe import simple_spread_v2"
agent-labels: "agents= [agent_0, agent_1, agent_2]"
---

<div class="docu-info" markdown="1">
{% include info_box.md %}
</div>

<div class="docu-content" markdown="1">
<div class="appear_big env-title" markdown="1">
{% include env_icon.md %}
## {{page.title}}
</div>




This environment has N agents, N landmarks (default N=3). At a high level, agents must learn to cover all the landmarks while avoiding collisions.

More specifically, all agents are globally rewarded based on how far the closest agent is to each landmark (sum of the minimum distances). Locally, the agents are penalized if they collide with other agents (-1 for each collision). The relative weights of these rewards can be controlled with the `local_ratio` parameter.

Agent observations: `[self_vel, self_pos, landmark_rel_positions, other_agent_rel_positions, communication]`

Agent action space: `[no_action, move_left, move_right, move_down, move_up]`

### Arguments

``` python
simple_spread_v2.env(N=3, local_ratio=0.5, max_cycles=25, continuous_actions=False)
```



`N`:  number of agents and landmarks

`local_ratio`:  Weight applied to local reward and global reward. Global reward weight will always be 1 - local reward weight.

`max_cycles`:  number of frames (a step for each agent) until game terminates

`continuous_actions`: Whether agent action spaces are discrete(default) or continuous
</div>