---
title: Wrapper
---

# Wrappers

## Using Wrappers

A wrapper is an environment transformation that takes in an environment as input, and outputs a new environment that is similar to the input environment, but with some transformation or validation applied.

The following wrappers can be used with PettingZoo environments:



[PettingZoo Wrappers](./wrappers/pz_wrappers.md) include [conversion wrappers](./wrappers/pz_wrappers.md#conversion-wrappers) to convert between the [AEC](./aec.md) and [Parallel](./parallel.md) APIs, and a set of simple [utility wrappers](./wrappers/pz_wrappers.md#utility-wrappers) which provide input validation and other convenient reusable logic.

[Supersuit Wrappers](/api/wrappers/supersuit_wrappers/) include commonly used pre-processing functions such as frame-stacking and color reduction, compatible with both PettingZoo and Gymnasium.

[Shimmy Compatibility Wrappers](/api/wrappers/shimmy_wrappers/) allow commonly used external reinforcement learning environments to be used with PettingZoo and Gymnasium.


```{toctree}
:hidden:
wrappers/pz_wrappers
wrappers/supersuit_wrappers
wrappers/shimmy_wrappers
```
