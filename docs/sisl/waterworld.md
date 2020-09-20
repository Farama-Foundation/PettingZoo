---
actions: "Continuous"
title: "Waterworld"
agents: "3"
manual-control: "No"
action-shape: "(2,)"
action-values: "(-1, 1)"
observation-shape: "(212,)"
observation-values: "[-10,10]"
average-total-reward: "-0.533"
import: "from pettingzoo.sisl import waterworld_v1"
agent-labels: "agents= ['pursuer_0', 'pursuer_1', ..., 'pursuer_4']"
---

{% include info_box.md %}



By default there are 5 agents (purple), 5 food targets (green) and 10 poison targets (red). Each agent has 30 range-limited sensors, depicted by the black lines, to detect neighboring agents (food and poison targets) resulting in 212 long vector of computed values about the environment for the observation space. They have a continuous action space represented as a 2 element vector, which corresponds to left/right and up/down thrust. The agents each receive a reward of 10 when more than one agent captures food together (the food is not destroyed), a shaping reward of 0.01 for touching food, a reward of -1 for touching poison, and a -0.5×｜action｜ reward when an agent collides into another. The environment runs for 500 frames by default. Observation shape takes the full form of ((4 + 3×speed_features)×n_sensors+2,).

This has been fixed from the reference environments to keep items floating off screen and being lost forever.

### Arguments

```
waterworld.env(n_pursuers=5, n_evaders=5, n_coop=2, n_poison=10, radius=0.015,
obstacle_radius=0.2, obstacle_loc=np.array([0.5, 0.5]), ev_speed=0.01,
poison_speed=0.01, n_sensors=30, sensor_range=0.2, action_scale=0.01,
poison_reward=-1., food_reward=10., encounter_reward=.01, control_penalty=-.5,
reward_mech=1.0, speed_features=True, max_frames=500)
```



`n_pursuers`:  number of pursuing archea

`n_evaders`:  number of evaders

`n_coop`:  how many archea touching food at same time for food to be considered consumed

`n_poison`:  number of poison objects

`radius`:  pursuer archea radius

`obstacle_radius`:  radius of obstacle object

`obstacle_loc`:  coordinate of obstacle object

`ev_speed`:  evading archea speed

`poison_speed`:  speed of poison object

`n_sensors`:  number of sensor dendrites on all archea

`sensor_range`:  length of sensor dendrite on all archea

`action_scale`:  scaling factor applied to all input actions

`poison_reward`:  reward for pursuer consuming a poison object

`food_reward`:  reward for pursuers consuming an evading archea

`encounter_reward`:  reward for a pursuer colliding with another archea

`control_penalty`:  reward added to pursuer in each step

`local_ratio`: Proportion of reward allocated locally vs distributed among all agents

`speed_features`:  toggles whether archea sensors detect speed of other objects

`max_frames`:  after max_frames steps all agents will return done
