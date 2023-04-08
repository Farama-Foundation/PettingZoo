---
title: Wrapper
---

# Wrappers

## Using Wrappers

A wrapper is an environment transformation that takes in an environment as input, and outputs a new environment that is similar to the input environment, but with some transformation or validation applied. PettingZoo provides [wrappers to convert environments](/api/wrappers/pz_wrappers) back and forth between the AEC API and the Parallel API and a set of simple [utility wrappers](/api/wrappers/pz_wrappers) which provide input validation and other convenient reusable logic. PettingZoo also includes [wrappers](/api/wrappers/supersuit_wrappers) via the SuperSuit companion package (`pip install supersuit`).

* [PettingZoo](/api/wrappers/pz_wrappers/): _PettingZoo wrappers_ 

* [Supersuit](/api/wrappers/supersuit_wrappers/): _Supersuit wrappers_ 

* [Shimmy](/api/wrappers/shimmy_wrappers/): _Shimmy wrappers_ 


```python
from pettingzoo.butterfly import pistonball_v6
from pettingzoo.utils import ClipOutOfBoundsWrapper

env = pistonball_v6.env()
wrapped_env = ClipOutOfBoundsWrapper(env)
# Wrapped environments must be reset before use
wrapped_env.reset()
```


```{toctree}
:hidden:
wrappers/pz_wrappers
wrappers/supersuit_wrappers
wrappers/shimmy_wrappers
```