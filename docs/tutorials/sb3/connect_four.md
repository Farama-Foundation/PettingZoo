---
title: "SB3: Action Masked PPO for Connect Four"
---

# SB3: Action Masked PPO for Connect Four

```{eval-rst}
.. warning::

   Currently, this tutorial doesn't work with versions of gymnasium>0.29.1. We are looking into fixing it but it might take some time.

```

This tutorial shows how to train a agents using Maskable [Proximal Policy Optimization](https://sb3-contrib.readthedocs.io/en/master/modules/ppo_mask.html) (PPO) on the [Connect Four](/environments/classic/chess/) environment ([AEC](/api/aec/)).

It creates a custom Wrapper to convert to a [Gymnasium](https://gymnasium.farama.org/)-like environment which is compatible with [SB3 action masking](https://sb3-contrib.readthedocs.io/en/master/modules/ppo_mask.html).

After training and evaluation, this script will launch a demo game using human rendering. Trained models are saved and loaded from disk (see SB3's [documentation](https://stable-baselines3.readthedocs.io/en/master/guide/save_format.html) for more information).

```{eval-rst}
.. note::

    This environment has a discrete (1-dimensional) observation space with an illegal action mask, so we use a masked MLP feature extractor.
```

```{eval-rst}
.. warning::

    The SB3ActionMaskWrapper wrapper assumes that the action space and observation space is the same for each agent, this assumption may not hold for custom environments.
```


## Environment Setup
To follow this tutorial, you will need to install the dependencies shown below. It is recommended to use a newly-created virtual environment to avoid dependency conflicts.
```{eval-rst}
.. literalinclude:: ../../../tutorials/SB3/connect_four/requirements.txt
   :language: text
```

## Code
The following code should run without any issues. The comments are designed to help you understand how to use PettingZoo with SB3. If you have any questions, please feel free to ask in the [Discord server](https://discord.gg/nhvKkYa6qX).

### Training and Evaluation

```{eval-rst}
.. literalinclude:: ../../../tutorials/SB3/connect_four/sb3_connect_four_action_mask.py
   :language: python
```

### Testing other PettingZoo Classic environments

The following script uses [pytest](https://docs.pytest.org/en/latest/) to test all other PettingZoo environments which support action masking.

This code yields decent results on simpler environments like [Connect Four](/environments/classic/connect_four/), while more difficult environments such as [Chess](/environments/classic/chess/) or [Hanabi](/environments/classic/hanabi/) will likely take much more training time and hyperparameter tuning.

```{eval-rst}
.. literalinclude:: ../../../tutorials/SB3/test/test_sb3_action_mask.py
   :language: python
```
