---
title: "Tianshou: Training Agents"
---

# Tianshou: Training Agents

This tutorial shows how to use [Tianshou](https://github.com/thu-ml/tianshou) to train a [Deep Q-Network](https://tianshou.readthedocs.io/en/master/tutorials/dqn.html) (DQN) agent to play vs a [random policy](https://tianshou.readthedocs.io/en/master/_modules/tianshou/policy/random.html) agent in the [Tic-Tac-Toe](/environments/classic/tictactoe/) environment.

## Environment Setup
To follow this tutorial, you will need to install the dependencies shown below. It is recommended to use a newly-created virtual environment to avoid dependency conflicts.
```{eval-rst}
.. literalinclude:: ../../../tutorials/Tianshou/requirements.txt
   :language: text
```

## Code
The following code should run without any issues. The comments are designed to help you understand how to use PettingZoo with CleanRL. If you have any questions, please feel free to ask in the [Discord server](https://discord.gg/nhvKkYa6qX).

```{eval-rst}
.. literalinclude:: ../../../tutorials/Tianshou/2_training_agents.py
   :language: python
```
