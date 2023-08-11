---
title: "CleanRL: Advanced PPO"
---

# CleanRL: Advanced PPO

This tutorial shows how to train [PPO](https://docs.cleanrl.dev/rl-algorithms/ppo/) agents on [Atari](/environments/butterfly/pistonball/) environments ([Parallel](/api/parallel/)).
This is a full training script including CLI, logging and integration with [TensorBoard](https://www.tensorflow.org/tensorboard) and [WandB](https://wandb.ai/) for experiment tracking.

This tutorial is mirrored from [CleanRL](https://github.com/vwxyzjn/cleanrl)'s examples. Full documentation and experiment results can be found at [https://docs.cleanrl.dev/rl-algorithms/ppo/#ppo_pettingzoo_ma_ataripy](https://docs.cleanrl.dev/rl-algorithms/ppo/#ppo_pettingzoo_ma_ataripy)

## Environment Setup
To follow this tutorial, you will need to install the dependencies shown below. It is recommended to use a newly-created virtual environment to avoid dependency conflicts.
```{eval-rst}
.. literalinclude:: ../../../tutorials/CleanRL/requirements.txt
   :language: text
```

Then, install ROMs using [AutoROM](https://github.com/Farama-Foundation/AutoROM), or specify the path to your Atari rom using the `rom_path` argument (see [Common Parameters](/environments/atari/#common-parameters)).

## Code
The following code should run without any issues. The comments are designed to help you understand how to use PettingZoo with CleanRL. If you have any questions, please feel free to ask in the [Discord server](https://discord.gg/nhvKkYa6qX), or create an issue on [CleanRL's GitHub](https://github.com/vwxyzjn/cleanrl/issues).
```{eval-rst}
.. literalinclude:: ../../../tutorials/CleanRL/cleanrl_advanced.py
   :language: python
```
