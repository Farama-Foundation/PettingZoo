---
title: "SB3: PPO for Pistonball (Parallel)"
---

# SB3: PPO for Pistonball

This tutorial shows how to train a [Proximal Policy Optimization](https://stable-baselines3.readthedocs.io/en/master/modules/ppo.html) (PPO) model on the [Pistonball](https://pettingzoo.farama.org/environments/butterfly/pistonball/) environment ([Parallel](https://pettingzoo.farama.org/api/parallel/)).

After training and evaluation, this script will launch a demo game using human rendering. Trained models are saved and loaded from disk (see SB3's [documentation](https://stable-baselines3.readthedocs.io/en/master/guide/save_format.html) for more information).

```{eval-rst}
.. note::

    This environment has a visual (3-dimensional) observation space, so we use a CNN feature extractor.
```

## Environment Setup
To follow this tutorial, you will need to install the dependencies shown below. It is recommended to use a newly-created virtual environment to avoid dependency conflicts.
```{eval-rst}
.. literalinclude:: ../../../tutorials/SB3/requirements.txt
   :language: text
```

## Code
The following code should run without any issues. The comments are designed to help you understand how to use PettingZoo with SB3. If you have any questions, please feel free to ask in the [Discord server](https://discord.gg/nhvKkYa6qX).

### Training and Evaluation

```{eval-rst}
.. literalinclude:: ../../../tutorials/SB3/pistonball/sb3_pistonball_vector.py
   :language: python
```
