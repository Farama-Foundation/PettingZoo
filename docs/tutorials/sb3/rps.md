---
title: "SB3: PPO for Rock-Paper-Scissors (AEC)"
---

# SB3: PPO for Rock-Paper-Scissors

This tutorial shows how to train a [Proximal Policy Optimization](https://stable-baselines3.readthedocs.io/en/master/modules/ppo.html) (PPO) model on the [Rock-Paper-Scissors](https://pettingzoo.farama.org/environments/classic/rps/) environment ([AEC](https://pettingzoo.farama.org/api/aec/)).

It converts the environment into a Parallel environment and uses SuperSuit to create vectorized environments, leveraging multithreading to speed up training.

After training, run the provided code to watch your trained agent play vs itself. See the [documentation](https://stable-baselines3.readthedocs.io/en/master/guide/save_format.html) for more information about saving and loading models.


## Environment Setup
To follow this tutorial, you will need to install the dependencies shown below. It is recommended to use a newly-created virtual environment to avoid dependency conflicts.
```{eval-rst}
.. literalinclude:: ../../../tutorials/SB3/requirements.txt
   :language: text
```

## Code
The following code should run without any issues. The comments are designed to help you understand how to use PettingZoo with SB3. If you have any questions, please feel free to ask in the [Discord server](https://discord.gg/nhvKkYa6qX).

### Training the RL agent

```{eval-rst}
.. literalinclude:: ../../../tutorials/SB3/sb3_rps.py
   :language: python
```

### Watching the trained RL agent play

```{eval-rst}
.. literalinclude:: ../../../tutorials/SB3/render_sb3_rps.py
   :language: python
```
