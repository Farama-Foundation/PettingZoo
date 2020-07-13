
### Gather

This environment is part of the [MAgent environments](../magent). Please read that page first for general information.

| Actions  | Agents | Manual Control | Action Shape    | Action Values           | Observation Shape        | Observation Values |
|----------|--------|----------------|-----------------|-------------------------|--------------------------|--------------------|
| Discrete | 495    | No             | (33)         | Discrete(33)     | (15,15,43)             | [0,2]              |

`pettingzoo.magent import gather_v0`

`agents= [ omnivore_[0-494] ]`

![](magent_gather.gif)

*AEC diagram*

In gather, the agents must survive by eating food or each other.

Action options:

* doing nothing
* moving to any of the 28 closest squares
* attacking any of the 4 closest squares.

Reward is given as:

* -0.01 reward every step
* -0.1 reward for attacking
* 0.5 reward for attacking an agent
* 5 reward for eating a food (requires multiple attacks)
* -1 reward for dying

```
gather_v0.env(seed=None)
```

```
seed: seed for random values. Set to None to use machine random source. Set to fixed value for deterministic behavior.
```
