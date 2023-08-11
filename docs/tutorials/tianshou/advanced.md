---
title: "Tianshou: CLI and Logging"
---

# Tianshou: CLI and Logging

This tutorial is a full example using Tianshou to train a [Deep Q-Network](https://tianshou.readthedocs.io/en/master/tutorials/dqn.html) (DQN) agent on the [Tic-Tac-Toe](/environments/classic/tictactoe/) environment.

It extends the code from [Training Agents](/tutorials/tianshou/intermediate/) to add CLI (using [argparse](https://docs.python.org/3/library/argparse.html)) and logging (using Tianshou's [Logger](https://tianshou.readthedocs.io/en/master/tutorials/logger.html)).


## Environment Setup
To follow this tutorial, you will need to install the dependencies shown below. It is recommended to use a newly-created virtual environment to avoid dependency conflicts.
```{eval-rst}
.. literalinclude:: ../../../tutorials/Tianshou/requirements.txt
   :language: text
```

## Code
The following code should run without any issues. The comments are designed to help you understand how to use PettingZoo with CleanRL. If you have any questions, please feel free to ask in the [Discord server](https://discord.gg/nhvKkYa6qX).

```{eval-rst}
.. literalinclude:: ../../../tutorials/Tianshou/3_cli_and_logging.py
   :language: python
```
