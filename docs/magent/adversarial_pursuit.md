
### Adversarial Pursuit

This environment is part of the [MAgent environments](../magent.md). Please read that page first for general information.

| Actions  | Agents | Manual Control | Action Shape    | Action Values           | Observation Shape        | Observation Values |
|----------|--------|----------------|-----------------|-------------------------|--------------------------|--------------------|
| Discrete | 75     | No             | (9),(13)     | Discrete(9),(13) | (10,10,19), (9,9,15)    | [0,2]              |

`pettingzoo.magent import adversarial_pursuit_v0`

`agents= [ predator_[0-24], prey_[0-49] ]`

![](magent_adversarial_pursuit.gif)

*AEC diagram*

The red agents must navigate the obstacles and try to trap the blue agents.

Predator action options:

* doing nothing
* Moving to any of the 4 closest squares
* attacking any of the 8 closest squares.

Predator's reward is given as:

* -0.2 reward for attacking
* 1 reward for attacking a prey

Prey action options:

* doing nothing
* moving to any of the 8 nearest squares

Prey's reward is given as:

* -1 reward for being attacked

```
adversarial_pursuit_v0.env(seed=None, map_size=45)
```

```
seed: seed for random values. Set to None to use machine random source. Set to fixed value for deterministic behavior.

map_size: size of each dimension of the map. Also affects the number of players on each team.
```
