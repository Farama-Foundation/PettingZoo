---
title: "Stable-Baselines3"
---

# Stable-Baselines3 Tutorial

These tutorials show you how to use the [Stable-Baselines3](https://stable-baselines3.readthedocs.io/en/master/) (SB3) library to train agents in PettingZoo environments.

For environments with visual observation spaces, we use a [CNN](https://stable-baselines3.readthedocs.io/en/master/modules/ppo.html#stable_baselines3.ppo.CnnPolicy) policy and perform pre-processing steps such as frame-stacking and resizing using [SuperSuit](/api/wrappers/supersuit_wrappers/).

* [PPO for Knights-Archers-Zombies](/tutorials/sb3/kaz/) _Train agents using PPO in a vectorized environment with visual observations_

For non-visual environments, we use [MLP](https://stable-baselines3.readthedocs.io/en/master/modules/ppo.html#stable_baselines3.ppo.MlpPolicy) policies and do not perform any pre-processing steps.

* [PPO for Waterworld](/tutorials/sb3/waterworld/): _Train agents using PPO in a vectorized environment with discrete observations_

* [Action Masked PPO for Connect Four](/tutorials/sb3/connect_four/): _Train agents using Action Masked PPO in an AEC environment_

```{eval-rst}
.. warning::

    Note: SB3 is designed for single-agent RL and does not directly support multi-agent algorithms or environments. These tutorials are only intended for demonstration purposes, to show how SB3 can be adapted to work with PettingZoo.
```

```{eval-rst}
.. note::

    These tutorials utilize PPO with parameter sharing, allowing a single model to control all the agents in an environment.

    For more information on PPO implementation details and multi-agent environments, see https://iclr-blog-track.github.io/2022/03/25/ppo-implementation-details/

        For example, if there is a two-player game, we can create a vectorized environment that spawns two sub-environments. Then, the vectorized environment produces a batch of two observations, where the first observation is from player 1 and the second observation is from player 2. Next, the vectorized environment takes a batch of two actions and tells the game engine to let player 1 execute the first action and player 2 execute the second action. Consequently, PPO learns to control both player 1 and player 2 in this vectorized environment.

```


## Stable-Baselines Overview

[Stable-Baselines3](https://stable-baselines3.readthedocs.io/en/master/) (SB3) is a library providing reliable implementations of reinforcement learning algorithms in [PyTorch](https://pytorch.org/). It provides a clean and simple interface, giving you access to off-the-shelf state-of-the-art model-free RL algorithms. It allows training of RL agents with only a few lines of code.

For more information, see the [Stable-Baselines3 v1.0 Blog Post](https://araffin.github.io/post/sb3/)


```{figure} https://raw.githubusercontent.com/DLR-RM/stable-baselines3/master/docs/_static/img/logo.png
    :alt: SB3 Logo
    :width: 80%
```

```{toctree}
:hidden:
:caption: SB3

kaz
waterworld
connect_four
```
