---
title: "RLlib"
---

# Ray RLlib Tutorial

These tutorials show you how to use [Ray](https://docs.ray.io/en/latest/index.html)'s [RLlib](https://docs.ray.io/en/latest/rllib/index.html) library to train agents in PettingZoo environments.

* [PPO for Pistonball](/tutorials/rllib/pistonball/): _Train PPO agents in a parallel environment_

* [DQN for Simple Poker](/tutorials/rllib/holdem/) _Train a DQN agent in an AEC environment_

##  RLlib Overview

[RLlib](https://github.com/ray-project/ray/tree/master/rllib) is an industry-grade open-source reinforcement learning library.
It is a part of [Ray](https://github.com/ray-project/ray), a popular library for distributed ML and scaling python applications.

See the [documentation](https://docs.ray.io/en/latest/rllib/index.html) for more information.
 * [PettingZoo Env](https://docs.ray.io/en/latest/rllib/rllib-env.html#pettingzoo-multi-agent-environments)
 * [Implemented Algorithms](https://docs.ray.io/en/latest/rllib/rllib-algorithms.html)

## Examples using PettingZoo:

### Training:
 * [supersuit preprocessing: pistonball](https://github.com/ray-project/ray/blob/master/rllib/examples/env/greyscale_env.py)
 * [simple multi-agent: rock-paper-scissors](https://github.com/ray-project/ray/blob/master/rllib/examples/rock_paper_scissors_multiagent.py)
 * [multi-agent parameter sharing: waterworld](https://github.com/ray-project/ray/blob/master/rllib/examples/multi_agent_parameter_sharing.py)
 * [multi-agent independent learning: waterworld](https://github.com/ray-project/ray/blob/master/rllib/examples/multi_agent_independent_learning.py)
 * [multi-agent leela chess zero](https://github.com/ray-project/ray/blob/master/rllib/examples/multi-agent-leela-chess-zero.py)

[//]: # (TODO: test waterworld, leela chess zero, add PR to pettingzoo if it isn't merged)

### Environments:
 * [connect four](https://github.com/ray-project/ray/blob/293fe2cb182b15499672c9cf50f79c8a9857dfb4/rllib/examples/env/pettingzoo_connect4.py)
 * [chess](https://github.com/ray-project/ray/blob/293fe2cb182b15499672c9cf50f79c8a9857dfb4/rllib/examples/env/pettingzoo_chess.py)

## Architecture

```{figure} https://docs.ray.io/en/latest/_images/rllib-stack.svg
    :alt: RLlib stack
    :width: 80%
```

```{toctree}
:hidden:
:caption: RLlib

pistonball
holdem
```

pistonball
holdem
```
