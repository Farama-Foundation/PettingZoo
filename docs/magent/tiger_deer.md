
### Tiger-Deer

This environment is part of the [MAgent environments](../magent.md). Please read that page first for general information.

| Actions  | Agents | Manual Control | Action Shape    | Action Values           | Observation Shape        | Observation Values |
|----------|--------|----------------|-----------------|-------------------------|--------------------------|--------------------|
| Discrete | 121    | No             | (5),(9)      | Discrete(5),(9)  | (3,3,21), (9,9,25)      | [0,2]              |

`pettingzoo.magent import tiger_deer_v0`

`agents= [ deer_[0-100], tiger_[0-19] ]`

![](magent_tiger_deer.gif)

*AEC diagram*

In tiger-deer, there are a number of tigers who must team up to take down the deer (two tigers must attack a deer in the same step to receive reward). If they do not eat the deer, they will not survive. At the same time, the deer are trying to avoid getting eaten.  

Tiger action options:

* doing nothing
* c to any of the 4 closest squares
* attacking any of the 4 closest squares.

Tiger's reward is given as:

* 1 reward for attacking a deer alongside another tiger

Deer action options:

* doing nothing
* moving to any of the 4 nearest squares

Deer's reward is given as:

* -1 reward for dying


```
tiger_deer_v0.env(seed=None, map_size=45)
```

```
seed: seed for random values. Set to None to use machine random source. Set to fixed value for deterministic behavior.

map_size: size of each dimension of the map. Also affects the number of players on each team.
```
