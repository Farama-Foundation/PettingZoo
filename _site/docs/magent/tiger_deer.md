
### Tiger-Deer

This environment is part of the [MAgent environments](magent). Please read that page first for general information.

| Actions  | Agents | Manual Control | Action Shape    | Action Values           | Observation Shape        | Observation Values |
|----------|--------|----------------|-----------------|-------------------------|--------------------------|--------------------|
| Discrete | 121    | No             | (5),(9)      | Discrete(5),(9)  | (3,3,21), (9,9,25)      | [0,2]              |

`pettingzoo.magent import tiger_deer_v0`

`agents= [ deer_[0-100], tiger_[0-19] ]`

![](docs/magent/magent_tiger_deer.gif)

*AEC diagram*

```
tiger_deer_v0.env(seed=None, map_size=100)
```

```
seed: seed for random values. Set to None to use machine random source. Set to fixed value for deterministic behavior.

map_size: size of each dimension of the map. Also affects the number of players on each team.
```
