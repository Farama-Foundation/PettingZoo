
### Combined Arms

This environment is part of the [MAgent environments](../magent.md). Please read that page first for general information.

| Actions  | Agents | Manual Control | Action Shape    | Action Values           | Observation Shape        | Observation Values |
|----------|--------|----------------|-----------------|-------------------------|--------------------------|--------------------|
| Discrete | 162    | No             | (9),(25)     | Discrete(9),(25) | (13,13,35), (13,13,51) | [0,2]              |

`pettingzoo.magent import combined_arms_v0`

`agents= [ redmelee_[0-44], redranged_[0-35], bluemelee_[0-44], blueranged_[0-35], ]`

![](magent_combined_arms.gif)

*AEC diagram*

```
combined_arms_v0.env(seed=None, map_size=45)
```

```
seed: seed for random values. Set to None to use machine random source. Set to fixed value for deterministic behavior.

map_size: size of each dimension of the map. Also affects the number of players on each team.
```
