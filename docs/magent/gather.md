---
actions: "Discrete"
title: "Gather"
agents: "495"
manual-control: "No"
action-shape: "(33)"
action-values: "Discrete(33)"
observation-shape: "(15,15,43)"
observation-values: "[0,2]"
---

### Gather

This environment is part of the [MAgent environments](../magent). Please read that page first for general information.

{% include table.md %}

[generally same fixes as all the others]


`pettingzoo.magent import gather_v0`

`agents= [ omnivore_[0-494] ]`

![](magent_gather.gif)

*AEC diagram*

In gather, the agents must gain reward by eating food or fighting each other. [talk about HP decay etc here like you did elsewhere]

Action options:

* doing nothing
* moving to any of the 28 closest squares
* attacking any of the 4 closest squares.

Reward is given as:

* -0.01 reward every step (shaped)
* -0.1 reward for attacking (shaped)
* -1 reward for dying (shaped)
* 1 reward for attacking an agent
* 5 reward for eating a food (requires multiple attacks)

```
gather_v0.env(seed=None, shape_reward=True)
```

```
seed: seed for random values. Set to None to use machine random source. Set to fixed value for deterministic behavior.

shape_reward: Set to False to remove all shaped reward (as shown in the lists above). This should be set when evaluating your agent.
```
