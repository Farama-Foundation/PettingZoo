---
title: Wrapper
---

# Wrappers

## Using Wrappers

A wrapper is an environment transformation that takes in an environment as input, and outputs a new environment that is similar to the input environment, but with some transformation or validation applied.

The following wrappers can be used with PettingZoo environments:



[PettingZoo Wrappers](/api/wrappers/pz_wrappers/) include [conversion wrappers](/api/wrappers/pz_wrappers#conversion-wrappers) to convert between the [AEC](/api/aec/) and [Parallel](/api/parallel/) APIs, and a set of simple [utility wrappers](/api/wrappers/pz_wrappers#utility-wrappers) which provide input validation and other convenient reusable logic.

[Supersuit Wrappers](/api/wrappers/supersuit_wrappers/) include commonly used pre-processing functions such as frame-stacking and color reduction, compatible with both PettingZoo and Gymnasium.

[Shimmy Compatibility Wrappers](/api/wrappers/shimmy_wrappers/) allow commonly used external reinforcement learning environments to be used with PettingZoo and Gymnasium.


```{toctree}
:hidden:
wrappers/pz_wrappers
wrappers/supersuit_wrappers
wrappers/shimmy_wrappers
```
