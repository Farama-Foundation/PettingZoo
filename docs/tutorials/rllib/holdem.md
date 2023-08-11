---
title: "RLlib: DQN for Simple Poker"
---

# RLlib: DQN for Simple Poker

This tutorial shows how to train a [Deep Q-Network](https://docs.ray.io/en/latest/rllib/rllib-algorithms.html#deep-q-networks-dqn-rainbow-parametric-dqn) (DQN) agent on the [Leduc Hold'em](/environments/classic/leduc_holdem/) environment ([AEC](/api/aec/)).

After training, run the provided code to watch your trained agent play vs itself. See the [documentation](https://docs.ray.io/en/latest/rllib/rllib-saving-and-loading-algos-and-policies.html) for more information.

## Environment Setup
To follow this tutorial, you will need to install the dependencies shown below. It is recommended to use a newly-created virtual environment to avoid dependency conflicts.
```{eval-rst}
.. literalinclude:: ../../../tutorials/Ray/requirements.txt
   :language: text
```

## Code
The following code should run without any issues. The comments are designed to help you understand how to use PettingZoo with RLlib. If you have any questions, please feel free to ask in the [Discord server](https://discord.gg/nhvKkYa6qX).

### Training the RL agent

```{eval-rst}
.. literalinclude:: ../../../tutorials/Ray/rllib_leduc_holdem.py
   :language: python
```

### Watching the trained RL agent play

```{eval-rst}
.. literalinclude:: ../../../tutorials/Ray/render_rllib_leduc_holdem.py
   :language: python
```
