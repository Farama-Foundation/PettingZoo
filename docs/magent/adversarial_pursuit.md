
### Adversarial Pursuit

This environment is part of the [MAgent environments](../magent.md). Please read that page first for general information.

| Actions  | Agents | Manual Control | Action Shape    | Action Values           | Observation Shape        | Observation Values |
|----------|--------|----------------|-----------------|-------------------------|--------------------------|--------------------|
| Discrete | 75     | No             | (9),(13)     | Discrete(9),(13) | (10,10,19), (9,9,15)    | [0,2]              |

`pettingzoo.magent import adversarial_pursuit_v0`

`agents= [ predator_[0-24], prey_[0-49] ]`

![](magent_adversarial_pursuit.gif)

*AEC diagram*

The red agents must navigate the obstacles and try to 

```
adversarial_pursuit_v0.env(seed=None, map_size=100)
```

```
seed: seed for random values. Set to None to use machine random source. Set to fixed value for deterministic behavior.

map_size: size of each dimension of the map. Also affects the number of players on each team.
```
