---
actions: "Discrete"
title: "Pursuit"
agents: "8 (+/-)"
manual-control: "Yes"
action-shape: "(5)"
action-values: "Discrete(5)"
observation-shape: "(7, 7, 3)"
observation-values: "[0, 30]"
average-total-reward: "30.3"
import: "from pettingzoo.sisl import pursuit_v3"
agent-labels: "agents= ['pursuer_0', 'pursuer_1', ..., 'pursuer_7']"
---

{% include info_box.md %}



By default 30 blue evader agents and 8 red pursuer agents are placed in a 16 x 16 grid with an obstacle, shown in white, in the center. The evaders move randomly, and the pursuers are controlled. Every time the pursuers fully surround an evader each of the surrounding agents receives a reward of 5 and the evader is removed from the environment. Pursuers also receive a reward of 0.01 every time they touch an evader. The pursuers have a discrete action space of up, down, left, right and stay. Each pursuer observes a 7 x 7 grid centered around itself, depicted by the orange boxes surrounding the red pursuer agents. The environment runs for 500 frames by default.  Note that this environment has already had the reward pruning optimization described in the *Agent Environment Cycle Games* paper applied.

Observation shape takes the full form of `(obs_range, obs_range, 3)` where the first channel is 1s where there is a wall, the second channel indicates the number of allies in each coordinate and the third channel indicates the number of opponents in each coordinate.

### Manual Control

Select different pursuers with 'J' and 'K'. The selected pursuer can be moved with the arrow keys.


### Arguments

```
pursuit.env(max_cycles=500, x_size=16, y_size=16, local_ratio=1.0, n_evaders=30, n_pursuers=8,
obs_range=7, n_catch=2, freeze_evaders=False, tag_reward=0.01, catch_reward=5.0,
urgency_reward=0.0, surround=True, constraint_window=1.0)

```

`x_size, y_size`: Size of environment world space

`local_ratio`: Proportion of reward allocated locally vs distributed among all agents

`n_evaders`:  Number of evaders

`n_pursuers`:  Number of pursuers

`obs_range`:  Size of the box around the agent that the agent observes.

`n_catch`:  Number pursuers required around an evader to be considered caught

`freeze_evaders`:  Toggles if evaders can move or not

`tag_reward`:  Reward for 'tagging', or being single evader.

`term_pursuit`:  Reward added when a pursuer or pursuers catch an evader

`urgency_reward`:  Reward to agent added in each step

`surround`:  Toggles whether evader is removed when surrounded, or when n_catch pursuers are on top of evader

`constraint_window`: Size of box (from center, in proportional units) which agents can randomly spawn into the environment world. Default is 1.0, which means they can spawn anywhere on the map. A value of 0 means all agents spawn in the center.

`max_cycles`:  After max_cycles steps all agents will return done
