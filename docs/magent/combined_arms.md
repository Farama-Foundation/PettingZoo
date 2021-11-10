---
actions: "Discrete"
title: "Combined Arms"
agents: "162"
manual-control: "No"
action-shape: "(9),(25)"
action-values: "Discrete(9),(25)"
observation-shape: "(13,13,9)"
observation-values: "[0,2]"
state-shape: "(45, 45, 9)"
state-values: "(0, 2)"
import: "from pettingzoo.magent import combined_arms_v5"
agent-labels: "agents= [redmelee_[0-44], redranged_[0-35], bluemelee_[0-44], blueranged_[0-35]]"
---

<div class="docu-info" markdown="1">
{% include info_box.md %}
</div>

<div class="docu-content" markdown="1">
<div class="appear_big env-title" markdown="1">
{% include env_icon.md %}
## {{page.title}}
</div>




A large-scale team battle. Here there are two types of agents on each team, ranged units which can attack farther and move faster but have less HP, and melee units which can only attack close units and move more slowly but have more HP. Unlike battle and battlefield, agents can attack units on their own team (they just are not rewarded for doing so). Agents slowly regain HP over time, so it is best to kill an opposing agent quickly. Specifically, agents have 10 HP, are damaged 2 HP by each attack, and recover 0.1 HP every turn.

### Arguments

``` python
combined_arms_v5.env(map_size=45, minimap_mode=False, step_reward=-0.005,
dead_penalty=-0.1, attack_penalty=-0.1, attack_opponent_reward=0.2, max_cycles=1000,
extra_features=False)
```

`map_size`: Sets dimensions of the (square) map. Increasing the size increases the number of agents. Minimum size is 16.

`minimap_mode`: Turns on global minimap observations. These observations include your and your opponents piece densities binned over the 2d grid of the observation space. Also includes your `agent_position`, the absolute position on the map (rescaled from 0 to 1).


`step_reward`:  reward after every step

`dead_penalty`:  reward when killed

`attack_penalty`:  reward when attacking anything

`attack_opponent_reward`:  reward added for attacking an opponent

`max_cycles`:  number of cycles (a step for each agent) until game terminates

`extra_features`: Adds additional features to observation (see table). Default False

#### Action Space

Key: `move_N` means N separate actions, one to move to each of the N nearest squares on the grid.

Melee action options: `[do_nothing, move_4, attack_4]`

Ranged action options: `[do_nothing, move_12, attack_12]`

#### Reward

Reward is given as:

* 5 reward for killing an opponent
* -0.005 reward every step (step_reward option)
* -0.1 reward for attacking (attack_penalty option)
* 0.2 reward for attacking an opponent (attack_opponent_reward option)
* -0.1 reward for dying (dead_penalty option)

If multiple options apply, rewards are added.

#### Observation space

The observation space is a 13x13 map with the below channels (in order):

feature | number of channels
--- | ---
obstacle/off the map| 1
my_team_presence| 1
my_team_hp| 1
my_team_minimap(minimap_mode=True)| 1
Other teams presences/heaths/minimaps (in some order) | 6 default/9 if minimap_mode=True
binary_agent_id(extra_features=True)| 10
one_hot_action(extra_features=True)| 9 Melee/25 ranged
last_reward(extra_features=True)| 1
agent_position(minimap_mode=True)| 2

### State space

The observation space is a 45x45 map. It contains the following channels, which are (in order):

feature | number of channels
--- | ---
obstacle map | 1
melee_team_1_presence | 1
melee_team_1_hp | 1
ranged_team_1_presence| 1
ranged_team_1_hp | 1
melee_team_2_presence | 1
melee_team_2_hp | 1
ranged_team_2_presence | 1
ranged_team_2_hp | 1
binary_agent_id(extra_features=True)| 10
one_hot_action(extra_features=True)|  25 (max action space)
last_reward(extra_features=True)| 1



### Version History

* v5: Fixed observation space order (1.9.0)
* v4: Fixed bugs and changed default parameters (1.7.0)
* v3: Added new arguments, fixes to observation space, changes to rewards (1.4.2)
* v2: Observation space bound fix, bumped version of all environments due to adoption of new agent iteration scheme where all agents are iterated over after they are done (1.4.0)
* v1: Agent order under death changed (1.3.0)
* v0: Initial versions release (1.0.0)
</div>