---
title: "SB3: Action Masked PPO for Connect Four"
---

# SB3: Action Masked PPO for Connect Four

This tutorial shows how to train a Maskable [Proximal Policy Optimization](https://sb3-contrib.readthedocs.io/en/master/modules/ppo_mask.html) (PPO) model on the [Connect Four](https://pettingzoo.farama.org/environments/classic/chess/) environment ([AEC](https://pettingzoo.farama.org/api/aec/)).

It creates a custom Wrapper to convert to a [Gymnasium](https://gymnasium.farama.org/)-like environment which is compatible with [SB3 action masking](https://sb3-contrib.readthedocs.io/en/master/modules/ppo_mask.html).


```{eval-rst}
.. note::

    This environment has a discrete (1-dimensional) observation space with an illegal action mask, so we use a masked MLP feature extractor.
```

```{eval-rst}
.. warning::

    This wrapper assumes that the action space and observation space is the same for each agent, this assumption may not hold for custom environments.
```

After training and evaluation, this script will launch a demo game using human rendering. Trained models are saved and loaded from disk (see SB3's [documentation](https://stable-baselines3.readthedocs.io/en/master/guide/save_format.html) for more information).


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

This code yields good results on simpler environments like [Gin Rummy](/environments/classic/gin_rummy/) and [Texas Hold’em No Limit](/environments/classic/texas_holdem_no_limit/), while failing to perform better than random in more difficult environments such as [Chess](/environments/classic/chess/) or [Hanabi](/environments/classic/hanabi/).


```{eval-rst}
.. literalinclude:: ../../../tutorials/SB3/test_sb3_action_mask.py
   :language: python
```
