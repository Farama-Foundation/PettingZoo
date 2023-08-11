---
title: "Tianshou: Basic API Usage"
---

# Tianshou: Basic API Usage

This tutorial is a simple example of how to use [Tianshou](https://github.com/thu-ml/tianshou) with a PettingZoo environment.

It demonstrates a game betwenen two [random policy](https://tianshou.readthedocs.io/en/master/_modules/tianshou/policy/random.html) agents in the [rock-paper-scissors](/environments/classic/rps/) environment.

## Environment Setup
To follow this tutorial, you will need to install the dependencies shown below. It is recommended to use a newly-created virtual environment to avoid dependency conflicts.
```{eval-rst}
.. literalinclude:: ../../../tutorials/Tianshou/requirements.txt
   :language: text
```

## Code
The following code should run without any issues. The comments are designed to help you understand how to use PettingZoo with Tianshou. If you have any questions, please feel free to ask in the [Discord server](https://discord.gg/nhvKkYa6qX).
```{eval-rst}
.. literalinclude:: ../../../tutorials/Tianshou/1_basic_api_usage.py
   :language: python
```
