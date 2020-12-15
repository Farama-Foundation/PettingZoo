---
actions: "Continuous"
title: "Waterworld"
agents: "3"
manual-control: "No"
action-shape: "(2,)"
action-values: "(-1, 1)"
observation-shape: "(212,)"
observation-values: "[-10,10]"
average-total-reward: "-14.5"
import: "from pettingzoo.sisl import waterworld_v2"
agent-labels: "agents= ['pursuer_0', 'pursuer_1', ..., 'pursuer_4']"

---

{% include info_box.md %}

Waterworld is a simulation of archea navigating and trying to survive in their environment. These archea are designated the roles of pursuer, evader, and poison. Pursuers attempt to consume evaders while avoiding poisons. Poisons have radii which are 0.75 times the size of the pursuer radius, while evaders have radii that are 2 the size of the pursuer radius. Depending on the input parameters, multiple archea may need to work together to consume an evader, creating a dynamic that is both cooperative and competitive. The environment is a continuous box space, and each archea has a position with x and y values each in the range [0,1]. The agents in this environment are the pursuers, while evaders and poison belong to the environment. Agents act by choosing a velocity vector to add to their current velocity. Each pursuer has a number of evenly spaced sensors which can read the speed and direction of objects relative to the pursuer. This information is reported in the observation space, and can be used to navigate the environment.

### Observation Space

The observation shape of each archea is a vector of length > 4 that is dependent on its input parameters. The full size of the vector is the number of features per sensor multiplied by the number of sensors, plus two elements indicating whether the archea collided with an evader or with a poison respectively. The number of features per sensor is 7 by default with `speed_features` enabled, or 4 if `speed_features` is turned off. Therefore with `speed_features` enabled, the observation shape takes the full form of `(7 × n_sensors) + 2`. Elements of the observation vector take on values in the range [-1, 1]. 

For example, by default there are 5 agents (purple), 5 food targets (green) and 10 poison targets (red). Each agent has 30 range-limited sensors, depicted by the black lines, to detect neighboring agents (food and poison targets) resulting in 212 long vector of computed values about the environment for the observation space. These values represent the distances and speeds sensed by each sensor on the archea. Sensors that do not sense any objects within their range report 0 for speed and 1 for distance.

This has been fixed from the reference environments to keep items floating off screen and being lost forever.

This table enumerates the observation space with `speed_features = True`:

|        Index: [start, end)        | Description                                  | Values  |
| :-------------------------------: | -------------------------------------------- | :-----: |
|           0 - n_sensors           | Obstacle distance for each sensor            | [0, 1]  |
|    n_sensors - (2 * n_sensors)    | Evader distance for each sensor              | [0, 1]  |
| (2 * n_sensors) - (3 * n_sensors) | Evader speed for each sensor                 | [-1, 1] |
| (3 * n_sensors) - (4 * n_sensors) | Poison distance for each sensor              | [0, 1]  |
| (4 * n_sensors) - (5 * n_sensors) | Poison speed for each sensor                 | [-1, 1] |
| (5 * n_sensors) - (6 * n_sensors) | Pursuer distance for each sensor             | [0, 1]  |
| (6 * n_sensors) - (7 * n_sensors) | Pursuer speed for each sensor                | [-1, 1] |
|          (7 * n_sensors)          | Indicates whether agent collided with evader | {0, 1}  |
|        (7 * n_sensors) + 1        | Indicates whether agent collided with poison | {0, 1}  |

This table enumerates the observation space with `speed_features = False`:

|        Index: [start, end)        | Description                                  | Values |
| :-------------------------------: | -------------------------------------------- | :----: |
|           0 - n_sensors           | Obstacle distance for each sensor            | [0, 1] |
|    n_sensors - (2 * n_sensors)    | Evader distance for each sensor              | [0, 1] |
| (2 * n_sensors) - (3 * n_sensors) | Poison distance for each sensor              | [0, 1] |
| (3 * n_sensors) - (4 * n_sensors) | Pursuer distance for each sensor             | [0, 1] |
|          (7 * n_sensors)          | Indicates whether agent collided with evader | {0, 1} |
|        (7 * n_sensors) + 1        | Indicates whether agent collided with poison | {0, 1} |

### Action Space

The archea have a continuous action space represented as a 2 element vector, which corresponds to horizontal and vertical thrust having values in the range [-1, 1]. This velocity vector is added to the archea's current velocity.

**Agent action space:** `[horizontal_velocity, vertical_velocity]`

### Rewards

By default, when multiple agents capture food together each agent receives a reward of 10 (the food is not destroyed). They receive a shaping reward of 0.01 for touching food, a reward of -1 for touching poison, and a -0.5 ×｜action｜ reward when they collide into another agent. The environment runs for 500 frames by default. 

### Arguments

```
waterworld.env(n_pursuers=5, n_evaders=5, n_coop=2, n_poison=10, radius=0.015,
obstacle_radius=0.2, obstacle_loc=np.array([0.5, 0.5]), ev_speed=0.01,
poison_speed=0.01, n_sensors=30, sensor_range=0.2, action_scale=0.01,
poison_reward=-1., food_reward=10., encounter_reward=.01, control_penalty=-.5,
local_ratio=1.0, speed_features=True, max_cycles=500)
```



`n_pursuers`:  number of pursuing archea (agents)

`n_evaders`:  number of evader archea

`n_coop`:  number of pursuing archea (agents) that must be touching food at the same time to consume it

`n_poison`:  number of poison archea

`radius`:  archea base radius

`obstacle_radius`:  radius of obstacle object

`obstacle_loc`:  coordinate of obstacle object

`ev_speed`:  evading archea speed

`poison_speed`:  poison archea object

`n_sensors`:  number of sensors on all pursuing archea (agents)

`sensor_range`:  length of sensor dendrite on all pursuing archea (agents)

`poison_reward`:  reward for pursuer consuming a poison object

`food_reward`:  reward for pursuers consuming an evading archea

`encounter_reward`:  reward for a pursuer colliding with an evading archea

`speed_penalty`:  scaling factor for the negative reward used to penalize large actions

`local_ratio`: Proportion of reward allocated locally vs distributed among all agents

`speed_features`:  toggles whether pursuing archea (agents) sensors detect speed of other archea

`max_cycles`:  After max_cycles steps all agents will return done