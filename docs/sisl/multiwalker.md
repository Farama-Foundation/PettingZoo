---
actions: "Continuous"
title: "Multiwalker"
alt_title: "MultiWalker"
agents: "3"
manual-control: "No"
action-shape: "(4,)"
action-values: "(-1, 1)"
observation-shape: "(31,)"
observation-values: "[-inf,inf]"
average-total-reward: "-300.86"
import: "from pettingzoo.sisl import multiwalker_v8"
agent-labels: "agents= ['walker_0', 'walker_1', 'walker_2']"
---

<div class="docu-info" markdown="1">
{% include info_box.md %}
</div>

<div class="docu-content" markdown="1">
<div class="appear_big env-title" markdown="1">
{% include env_icon.md %}
## {{page.title}}
</div>


In this environment, bipedal robots attempt to carry a package as far right as possible. A package is placed on top of 3 (by default) bipedal robots which you control. A positive reward is awarded to each walker, which is the change in the package distance summed with 130 times the change in the walker's position. The maximum achievable total reward depends on the terrain length; as a reference, for a terrain length of 75 steps with the scaling factor of 130, the total reward under an optimal policy is around 300 . If `shared_reward` is chosen (True by default), all agents receive the mean reward across agents. The agents also receive a small shaped reward of -5 times the change in their head angle to keep the head straight.

If a walker falls, it is penalized -10. By default, the environment is done if any walker or the package falls, or if the package goes beyond the left edge of the terrain. In all of these cases, each walker receives an additional reward of -100. If the `terminate_on_fall` setting is set to False, the game continues until the package falls. If the `remove_on_fall` setting is set to True, the walkers are removed from the environment after they fall. The environment is also done if package falls off the right edge of the terrain, with no additional reward or penalty.

Each walker exerts force on two joints in their two legs, giving a continuous action space represented as a 4 element vector. Each walker observes via a 31 element vector containing simulated noisy lidar data about the environment and information about neighboring walkers. The environment's duration is capped at 500 frames by default (can be controlled by the `max_cycles` setting).



### Observation Space

Each agent receives an observation composed of various physical properties of its legs and joints, as well as LIDAR readings from the space immediately in front and below the robot. The observation also includes information about neighboring walkers, and the package, which have normally distributed signal noise controlled by `position_noise` and `angle_noise`. For walkers without neighbors, observations about neighbor positions are zero.



This table enumerates the observation space:

| Index: [start, end) | Description                                                  |   Values    |
|:-----------------:|------------------------------------------------------------|:---------------:|
|          0          | Hull angle                |  [0, 2*pi]  |
|          1          | Hull angular velocity                                        | [-inf, inf] |
|          2          | X Velocity                                                   |   [-1, 1]   |
|          3          | Y Velocity                                                   |   [-1, 1]   |
|          4          | Hip joint 1 angle                                            | [-inf, inf] |
|          5          | Hip joint 1 speed                                            | [-inf, inf] |
|          6          | Knee joint 1 angle                                           | [-inf, inf] |
|          7          | Knee joint 1 speed                                           | [-inf, inf] |
|          8          | Leg 1 ground contact flag                                    |   {0, 1}    |
|          9          | Hip joint 1 angle                                            | [-inf, inf] |
|         10          | Hip joint 2 speed                                            | [-inf, inf] |
|         11          | Knee joint 2 angle                                           | [-inf, inf] |
|         12          | Knee joint 2 speed                                           | [-inf, inf] |
|         13          | Leg 2 ground contact flag                                    |   {0, 1}    |
|        14-23        | LIDAR sensor readings                                        | [-inf, inf] |
|         24          | Left neighbor relative X position (0.0 for leftmost walker) (Noisy) | [-inf, inf] |
|         25          | Left neighbor relative Y position (0.0 for leftmost walker) (Noisy) | [-inf, inf] |
|         26          | Right neighbor relative X position (0.0 for rightmost walker) (Noisy) | [-inf, inf] |
|         27          | Right neighbor relative Y position (0.0 for rightmost walker) (Noisy) | [-inf, inf] |
|         28          | Walker X position relative to package (0 for left edge, 1 for right edge) | [-inf, inf] |
|         29          | Walker Y position relative to package                        | [-inf, inf] |
|         30          | Package angle                                                | [-inf, inf] |

### Arguments

``` python
multiwalker_v8.env(n_walkers=3, position_noise=1e-3, angle_noise=1e-3, forward_reward=1.0, terminate_reward=-100.0, fall_reward=-10.0, shared_reward=True,
terminate_on_fall=True, remove_on_fall=True, terrain_legth=200, max_cycles=500)
```



`n_walkers`:  number of bipedal walker agents in environment

`position_noise`:  noise applied to agent positional sensor observations

`angle_noise`:  noise applied to agent rotational sensor observations

`forward_reward`:  reward applied for an agent standing, scaled by agent's x coordinate

`fall_reward`:  reward applied when an agent falls down

`shared_reward`:  whether reward is distributed among all agents or allocated locally

`terminate_reward`: reward applied to a walker for failing the environment

`terminate_on_fall`: toggles whether agent is done if it falls down

`remove_on_fall`: Remove walker when it falls (only does anything when `terminate_on_fall` is False)

`terrain_length`: length of terrain in number of steps

`max_cycles`:  after max_cycles steps all agents will return done


### Version History
* v8: Replaced local_ratio, fixed rewards, terrain length as an argument and documentation (1.15.0)
* v7: Fixed problem with walker collisions (1.8.2)
* v6: Fixed observation space and made large improvements to code quality (1.5.0)
* v5: Fixes to reward structure, added arguments (1.4.2)
* v4: Misc bug fixes (1.4.0)
* v3: Fixes to observation space (1.3.3)
* v2: Various fixes and environment argument changes (1.3.1)
* v1: Fixes to how all environments handle premature death (1.3.0)
* v0: Initial versions release (1.0.0)
</div>
