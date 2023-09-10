---
title: "CleanRL: Implementing PPO"
---

# CleanRL: Implementing PPO

This tutorial shows how to train [PPO](https://docs.cleanrl.dev/rl-algorithms/ppo/) agents on the [Pistonball](/environments/butterfly/pistonball/) environment ([Parallel](/api/parallel/)).

## Environment Setup
To follow this tutorial, you will need to install the dependencies shown below. It is recommended to use a newly-created virtual environment to avoid dependency conflicts.
```{eval-rst}
.. literalinclude:: ../../../tutorials/CleanRL/requirements.txt
   :language: text
```

## Code
The following code should run without any issues. The comments are designed to help you understand how to use PettingZoo with CleanRL. If you have any questions, please feel free to ask in the [Discord server](https://discord.gg/nhvKkYa6qX).
```{eval-rst}
.. literalinclude:: ../../../tutorials/CleanRL/cleanrl.py
   :language: python
```
