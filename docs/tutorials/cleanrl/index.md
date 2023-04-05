---
title: "CleanRL"
---

# CleanRL Tutorial

This tutorial shows how to use [CleanRL](https://github.com/vwxyzjn/cleanrl) to implement a model and train it on a PettingZoo environment. 

* [Implementing PPO](/tutorials/cleanrl/implementing_PPO.md): _Implement and train a PPO model_


## CleanRL Overview

[CleanRL](https://github.com/vwxyzjn/cleanrl) is a lightweight, highly-modularized reinforcement learning library, providing high-quality single-file implementations with research-friendly features. 


See the [documentation](https://docs.cleanrl.dev/) for more information. 

## Official examples using PettingZoo:

* [PPO PettingZoo Atari example](https://docs.cleanrl.dev/rl-algorithms/ppo/#ppo_pettingzoo_ma_ataripy)


## WandB Integration

A key feature is its tight integration with [Weights & Biases](https://wandb.ai/) (WandB): for experiment tracking, hyperparameter tuning, and benchmarking. 
The [Open RL Benchmark](https://github.com/openrlbenchmark/openrlbenchmark) allows users to view public leaderboards for many tasks, including videos of agents' performance across training timesteps.


```{figure} /_static/img/tutorials/cleanrl-wandb.png
    :alt: CleanRl integration with Weights & Biases
    :width: 80%
```


```{toctree}
:hidden:
:caption: CleanRL

implementing_PPO
```
