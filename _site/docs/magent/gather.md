
### Gather

This environment is part of the [MAgent environments](magent). Please read that page first for general information.

| Actions  | Agents | Manual Control | Action Shape    | Action Values           | Observation Shape        | Observation Values |
|----------|--------|----------------|-----------------|-------------------------|--------------------------|--------------------|
| Discrete | 495    | No             | (33)         | Discrete(33)     | (15,15,43)             | [0,2]              |

`pettingzoo.magent import gather_v0`

`agents= [ omnivore_[0-494] ]`

![](docs/magent/magent_gather.gif)

*AEC diagram*

```
gather_v0.env(seed=None)
```

```
seed: seed for random values. Set to None to use machine random source. Set to fixed value for deterministic behavior.
```
