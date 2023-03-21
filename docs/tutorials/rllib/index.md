---
title: "RLlib"
---

# RLlib Tutorial

These tutorials guide you through training and rendering PettingZoo environments using RLlib.

### [PPO for Pistonball (Parallel)](/tutorials/rllib/pistonball/)

### [DQN for Simple Poker (AEC)](/tutorials/rllib/holdem/)

##  RLlib Overview

```{figure} https://docs.ray.io/en/latest/_images/rllib-stack.svg
    :alt: RLlib stack
    :width: 70%
```

[RLlib](https://github.com/ray-project/ray/tree/master/rllib) is an industry-grade open-source reinforcement learning library.
It is a part of [Ray](https://github.com/ray-project/ray), a popular library for distributed ML and scaling python applications.

See the [documentation](https://docs.ray.io/en/latest/rllib/index.html) for more information.
 * [PettingZoo Env](https://docs.ray.io/en/latest/rllib/rllib-env.html#pettingzoo-multi-agent-environments)
 * [Implemented Algorithms](https://docs.ray.io/en/latest/rllib/rllib-algorithms.html)

## Official examples using PettingZoo:

### Training:
 * [simple multi-agent: rock-paper-scissors](https://github.com/ray-project/ray/blob/master/rllib/examples/rock_paper_scissors_multiagent.py)
 * [multi-agent parameter sharing: waterworld](https://github.com/ray-project/ray/blob/master/rllib/examples/multi_agent_parameter_sharing.py)
 * [multi-agent independent learning: waterworld](https://github.com/ray-project/ray/blob/master/rllib/examples/multi_agent_independent_learning.py)
 * [multi-agent leela chess zero](https://github.com/ray-project/ray/blob/master/rllib/examples/multi-agent-leela-chess-zero.py) 
 * [PR: connect four self-play with pettingzoo](https://github.com/ray-project/ray/pull/33481) 

[//]: # (TODO: test waterworld, leela chess zero, add PR to pettingzoo if it isn't merged)

### Environments
 * [connect four](https://github.com/ray-project/ray/blob/293fe2cb182b15499672c9cf50f79c8a9857dfb4/rllib/examples/env/pettingzoo_connect4.py)
 * [chess](https://github.com/ray-project/ray/blob/293fe2cb182b15499672c9cf50f79c8a9857dfb4/rllib/examples/env/pettingzoo_chess.py)


```{toctree}
:hidden:
:caption: RLlib

pistonball
holdem
```