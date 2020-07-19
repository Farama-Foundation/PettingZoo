---
layout: "docu"
title: "Tiger-Deer"
actions: "Discrete"
agents: "121"
manual-control: "No"
action-shape: "(5),(9)"
action-values: "Discrete(5),(9)"
observation-shape: "(3,3,21), (9,9,25)"
observation-values: "[0,2]"
---

### Tiger-Deer

This environment is part of the [MAgent environments](../magent). Please read that page first for general information.

{% include table.md %}

[same fixes as all the others]

`pettingzoo.magent import tiger_deer_v0`

`agents= [ deer_[0-100], tiger_[0-19] ]`

![](magent_tiger_deer.gif)

*AEC diagram*

In tiger-deer, there are a number of tigers who must team up to take down the deer (two tigers must attack a deer in the same step to receive reward). If they do not eat the deer, they will not survive. At the same time, the deer are trying to avoid getting attacked.  

Tiger action options:

* doing nothing
* c to any of the 4 closest squares
* attacking any of the 4 closest squares.

Tiger's reward is given as:

* 1 reward for attacking a deer alongside another tiger

Deer action options:

* doing nothing
* moving to any of the 4 nearest squares

Deer's reward is given as:

* -1 reward for dying

Observation space: `[empty, obstacle, deer, tigers, binary_agent_id(10), one_hot_action, last_reward]`

Map size: 45x45

```
tiger_deer_v0.env(seed=None)
```

```
seed: seed for random values. Set to None to use machine random source. Set to fixed value for deterministic behavior.
```
