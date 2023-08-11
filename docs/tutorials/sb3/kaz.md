---
title: "SB3: PPO for Knights-Archers-Zombies"
---

# SB3: PPO for Knights-Archers-Zombies

This tutorial shows how to train agents using [Proximal Policy Optimization](https://stable-baselines3.readthedocs.io/en/master/modules/ppo.html) (PPO) on the [Knights-Archers-Zombies](/environments/butterfly/knights_archers_zombies/) environment ([AEC](/api/aec/)).

We use SuperSuit to create vectorized environments, leveraging multithreading to speed up training (see SB3's [vector environments documentation](https://stable-baselines3.readthedocs.io/en/master/guide/vec_envs.html)).

After training and evaluation, this script will launch a demo game using human rendering. Trained models are saved and loaded from disk (see SB3's [model saving documentation](https://stable-baselines3.readthedocs.io/en/master/guide/save_format.html)).

If the observation space is visual (`vector_state=False` in `env_kwargs`), we pre-process using color reduction, resizing, and frame stacking, and use a [CNN](https://stable-baselines3.readthedocs.io/en/master/modules/ppo.html#stable_baselines3.ppo.CnnPolicy) policy.

```{eval-rst}
.. note::

    This environment has a visual (3-dimensional) observation space, so we use a CNN feature extractor.
```

```{eval-rst}
.. note::

    This environment allows agents to spawn and die, so it requires using SuperSuit's Black Death wrapper, which provides blank observations to dead agents rather than removing them from the environment.
```


## Environment Setup
To follow this tutorial, you will need to install the dependencies shown below. It is recommended to use a newly-created virtual environment to avoid dependency conflicts.
```{eval-rst}
.. literalinclude:: ../../../tutorials/SB3/kaz/requirements.txt
   :language: text
```

## Code
The following code should run without any issues. The comments are designed to help you understand how to use PettingZoo with SB3. If you have any questions, please feel free to ask in the [Discord server](https://discord.gg/nhvKkYa6qX).

### Training and Evaluation

```{eval-rst}
.. literalinclude:: ../../../tutorials/SB3/kaz/sb3_kaz_vector.py
   :language: python
```
