---
title: "SB3: PPO for Waterworld (Parallel)"
---

# SB3: PPO for Waterworld

This tutorial shows how to train agents using [Proximal Policy Optimization](https://stable-baselines3.readthedocs.io/en/master/modules/ppo.html) (PPO) on the [Waterworld](/environments/sisl/waterworld/) environment ([Parallel](/api/parallel/)).

We use SuperSuit to create vectorized environments, leveraging multithreading to speed up training (see SB3's [vector environments documentation](https://stable-baselines3.readthedocs.io/en/master/guide/vec_envs.html)).

After training and evaluation, this script will launch a demo game using human rendering. Trained models are saved and loaded from disk (see SB3's [model saving documentation](https://stable-baselines3.readthedocs.io/en/master/guide/save_format.html)).
```{eval-rst}
.. note::

    This environment has a discrete (1-dimensional) observation space, so we use an MLP feature extractor.
```


## Environment Setup
To follow this tutorial, you will need to install the dependencies shown below. It is recommended to use a newly-created virtual environment to avoid dependency conflicts.
```{eval-rst}
.. literalinclude:: ../../../tutorials/SB3/waterworld/requirements.txt
   :language: text
```

## Code
The following code should run without any issues. The comments are designed to help you understand how to use PettingZoo with SB3. If you have any questions, please feel free to ask in the [Discord server](https://discord.gg/nhvKkYa6qX).

### Training and Evaluation

```{eval-rst}
.. literalinclude:: ../../../tutorials/SB3/waterworld/sb3_waterworld_vector.py
   :language: python
```
