---
layout: "docu"
actions: "Discrete"
agents: "162"
manual-control: "No"
action-shape: "(9),(25)"
action-values: "Discrete(9),(25)"
observation-shape: "(13,13,35), (13,13,51)"
observation-values: "[0,2]"
---

### Combined Arms

This environment is part of the [MAgent environments](../magent). Please read that page first for general information.

{% include table.md %}


`pettingzoo.magent import combined_arms_v0`

`agents= [ redmelee_[0-44], redranged_[0-35], bluemelee_[0-44], blueranged_[0-35], ]`

![](magent_combined_arms.gif)

*AEC diagram*

A large-scale team battle. Here there are two types of agents on each team, ranged units which can attack father and move faster but have less HP, and melee units which can only attack close units and move more slowly but have more HP. Unlike battle and battlefield, agents can attack units on their own team (they just are not rewarded for doing so).

Melee action options:

* doing nothing
* moving to any of the 4 closest squares
* attacking any of the 4 closest squares.

Ranged action options:

* doing nothing
* moving to any of the 12 closest squares
* attacking any of the 12 closest squares.

Reward is given as:

* -0.01 reward for not attacking (shaped)
* -1 reward for attacking nothing (shaped)
* 2 reward for attacking an opponent (shaped)
* -1 reward for dying (shaped)
* 100 reward for killing an opponent

If multiple options apply, the rewards are simply added together (so for example, attacking an opponent that does not die will give 0.99 reward)

```
combined_arms_v0.env(seed=None, shape_reward=True)
```

```
seed: seed for random values. Set to None to use machine random source. Set to fixed value for deterministic behavior.

shape_reward: Set to False to remove all shaped reward (as shown in the lists above). This should be set when evaluating your agent.
```
