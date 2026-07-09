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

## Interpretable Predictive Policy

KAZ's vector observation also supports a compact policy that is useful as a
reproducible benchmark. The controller prioritizes zombies nearest the bottom
of the board, gives the two archers separate targets when possible, and solves
a projectile-intercept equation before firing. A small grid search calibrates
the lead and alignment thresholds; no model checkpoint is required.

```{figure} kaz_predictive_policy.gif
:width: 400px
:name: kaz-predictive-policy

Predictive policy on seed 2000, selected automatically as a median-reward
episode from the evaluation block rather than for appearance.
```

The following command searches on seeds 0 through 9, evaluates on the disjoint
seed block 2000 through 2049, and renders the representative GIF:

```bash
python tutorials/SB3/kaz/predictive_kaz_policy.py \
  --search --search-episodes 10 \
  --episodes 50 --eval-start 2000 \
  --render-gif docs/tutorials/sb3/kaz_predictive_policy.gif
```

On the environment defaults used by the script (`max_cycles=900`,
`max_zombies=10`), the frozen policy averaged 43.60 reward on those 50 held-out
seeds. A deterministically seeded random-action policy averaged 2.44. The
paired mean improvement was 41.16 with a bootstrap 95% confidence interval of
[40.62, 41.66].

```{eval-rst}
.. literalinclude:: ../../../tutorials/SB3/kaz/predictive_kaz_policy.py
   :language: python
```
