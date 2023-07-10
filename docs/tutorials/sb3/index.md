---
title: "Stable-Baselines3"
---

# Stable-Baselines3 Tutorial

These tutorials show you how to use the [SB3](https://stable-baselines3.readthedocs.io/en/master/) library to train agents in PettingZoo environments.

For environments with visual observations, we use a [CNN](https://stable-baselines3.readthedocs.io/en/master/modules/ppo.html#stable_baselines3.ppo.CnnPolicy) policy and perform pre-processing steps such as frame-stacking, color reduction, and resizing using [SuperSuit](/api/wrappers/supersuit_wrappers/)

* [PPO for Pistonball](/tutorials/sb3/pistonball/): _Train agents using PPO in vectorized Parallel environment_

* [PPO for Knights-Archers-Zombies](/tutorials/sb3/kaz/) _Train agents using PPO in a vectorized AEC environment_

For non-visual environments, we use [Actor Critic](https://stable-baselines3.readthedocs.io/en/master/modules/ppo.html#stable_baselines3.ppo.CnnPolicy) or [Maskable Actor Critic](https://sb3-contrib.readthedocs.io/en/master/modules/ppo_mask.html#maskableppo-policies) policies and do not perform any pre-processing steps.

* [PPO for Multiwalker](/tutorials/sb3/multiwalker/): _Train agents using PPO in a vectorized AEC environment_

* [Action Masked PPO for Connect Four](/tutorials/sb3/connect_four/): _Train an agent using Action Masked PPO in an AEC environment_


## Stable-Baselines Overview

[Stable-Baselines3](https://stable-baselines3.readthedocs.io/en/master/) (SB3) is a library providing reliable implementations of reinforcement learning algorithms in [PyTorch](https://pytorch.org/). It provides a clean and simple interface, giving you access to off-the-shelf state-of-the-art model-free RL algorithms. It allows training of RL agents with only a few lines of code.

For more information, see the [Stable-Baselines3 v1.0 Blog Post](https://araffin.github.io/post/sb3/)


```{eval-rst}
.. warning::

    Note: SB3 is designed for single-agent RL and does not plan on natively supporting multi-agent PettingZoo environments. These tutorials are only intended for demonstration purposes, to show how SB3 can be adapted to work in multi-agent settings.
```


```{figure} https://raw.githubusercontent.com/DLR-RM/stable-baselines3/master/docs/_static/img/logo.png
    :alt: SB3 Logo
    :width: 80%
```

```{toctree}
:hidden:
:caption: SB3

pistonball
kaz
multiwalker
connect_four
```
