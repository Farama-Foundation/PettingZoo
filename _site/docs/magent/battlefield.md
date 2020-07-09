
### Battlefield

This environment is part of the [MAgent environments](magent). Please read that page first for general information.

| Actions  | Agents | Manual Control | Action Shape    | Action Values           | Observation Shape        | Observation Values |
|----------|--------|----------------|-----------------|-------------------------|--------------------------|--------------------|
| Discrete | 24     | No             | (21)         | Discrete(21)     | (13,13,41)             | [0,2]              |

`pettingzoo.magent import battlefield_v0`

`agents= [ red_[0-11], blue_[0-11] ]`

![](docs/magent/magent_battlefield.gif)

*AEC diagram*

```
battlefield_v0.env(seed=None, map_size=100)
```

```
seed: seed for random values. Set to None to use machine random source. Set to fixed value for deterministic behavior.

map_size: size of each dimension of the map. Also affects the number of players on each team.
```
