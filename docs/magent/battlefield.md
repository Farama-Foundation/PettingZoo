
### Battlefield

This environment is part of the [MAgent environments](../magent). Please read that page first for general information.

| Actions  | Agents | Manual Control | Action Shape    | Action Values           | Observation Shape        | Observation Values |
|----------|--------|----------------|-----------------|-------------------------|--------------------------|--------------------|
| Discrete | 24     | No             | (21)         | Discrete(21)     | (13,13,41)             | [0,2]              |

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
