---
layout: docu
actions: Discrete
agents: 24
manual-control: No
action-shape: (21)
action-values: Discrete(21)
observation-shape: (13,13,41)
observation-values: [0,2]
---

### Battlefield

This environment is part of the [MAgent environments](../magent). Please read that page first for general information.


`pettingzoo.magent import battlefield_v0`

`agents= [ red_[0-11], blue_[0-11] ]`

![](magent_battlefield.gif)

*AEC diagram*

Same as [battle](./battle) but with fewer agents arrayed in a larger space with obstacles.

```
battlefield_v0.env(seed=None)
```

```
seed: seed for random values. Set to None to use machine random source. Set to fixed value for deterministic behavior.
```
