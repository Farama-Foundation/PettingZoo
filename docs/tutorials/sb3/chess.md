---
title: "SB3: Action Masked PPO for Chess"
---

# SB3: Action Masked PPO for Chess

This tutorial shows how to train a Maskable [Proximal Policy Optimization](https://sb3-contrib.readthedocs.io/en/master/modules/ppo_mask.html) (PPO) model on the [Chess](https://pettingzoo.farama.org/environments/classic/chess/) environment ([AEC](https://pettingzoo.farama.org/api/aec/)).

It creates a custom Wrapper to convert to a Gymnasium-like environment which is compatible with SB3's action masking format.

Note: This assumes that the action space and observation space is the same for each agent, this assumption may not hold for custom environments.

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
.. literalinclude:: ../../../tutorials/SB3/sb3_chess_action_mask.py
   :language: python
```

### Watching the trained RL agent play

```{eval-rst}
.. literalinclude:: ../../../tutorials/SB3/render_sb3_chess_action_mask.py
   :language: python
```
