---
title: "RLLib 2: RL for Simple Poker"
---

# RLLib 2: RL for Simple Poker

## Environment Setup
To follow this tutorial, you will need to install the dependencies shown below. It is recommended to use a newly-created virtual environment to avoid dependency conflicts.
```{eval-rst}
.. literalinclude:: ../../../tutorials/Ray/requirements.txt
   :language: text
```

## Code
The following code should run without any issues. The comments are designed to help you understand how to use PettingZoo with RLLib 2. If you have any questions, please feel free to ask in the [Discord server](https://discord.gg/nhvKkYa6qX).

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
