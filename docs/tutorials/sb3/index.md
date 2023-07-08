---
title: "Stable-Baselines3"
---

# Stable-Baselines3 Tutorial

These tutorials show you how to use the [SB3](https://stable-baselines3.readthedocs.io/en/master/) library to train agents in PettingZoo environments.

* [PPO for Pistonball](/tutorials/sb3/pistonball/): _Train a PPO model in vectorized Parallel environments_

* [PPO for Rock-Paper-Scissors](/tutorials/sb3/rps/) _Train a PPO model in vectorized AEC environments_

* [Action Masked PPO for Chess](/tutorials/sb3/chess/): _Train an action masked PPO model in an AEC environment_


## Stable-Baselines Overview

[Stable-Baselines3](https://stable-baselines3.readthedocs.io/en/master/) (SB3) is a library providing reliable implementations of reinforcement learning algorithms in [PyTorch](https://pytorch.org/). It provides a clean and simple interface, giving you access to off-the-shelf state-of-the-art model-free RL algorithms. It allows training of RL agents with only a few lines of code.

For more information, see the [Stable-Baselines3 v1.0 Blog Post](https://araffin.github.io/post/sb3/)

Note: SB3 does not officially support PettingZoo, as it is designed for single-agent RL. These tutorials demonstrate how to adapt SB3 to work in multi-agent settings, but we cannot guarantee training convergence.


```{figure} https://raw.githubusercontent.com/DLR-RM/stable-baselines3/master/docs/_static/img/logo.png
    :alt: SB3 Logo
    :width: 80%
```

```{toctree}
:hidden:
:caption: SB3

pistonball
rps
chess
```
