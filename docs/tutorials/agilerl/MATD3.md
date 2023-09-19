# AgileRL: Implementing MATD3
This tutorial shows how to train an [MATD3](https://agilerl.readthedocs.io/en/latest/api/algorithms/matd3.html) agent on the [simple speaker listener](https://pettingzoo.farama.org/environments/mpe/simple_speaker_listener/) multi-particle environment.

## What is MATD3?
[MATD3](https://agilerl.readthedocs.io/en/latest/api/algorithms/matd3.html) (Multi-Agent Twin Delayed Deep Deterministic Policy Gradients) extends the [MADDPG](https://agilerl.readthedocs.io/en/latest/api/algorithms/maddpg.html) (Multi-Agent Deep Deterministic Policy Gradients) algorithm to reduce overestimation bias in multi-agent domains through the use of a second set of critic networks and delayed updates of the policy networks. This enables superior performance when compared to MADDPG. For further information on MATD3, check out the AgileRL [documentation](https://agilerl.readthedocs.io/en/latest/api/algorithms/matd3.html).

### Can I use it?

|   | Action Space | Observation Space |
|---|--------------|-------------------|
|Discrete  | ✔️           | ✔️                |
|Continuous   | ✔️           | ✔️                |

## Environment Setup

To follow this tutorial, you will need to install the dependencies shown below. It is recommended to use a newly-created virtual environment to avoid dependency conflicts.
```{eval-rst}
.. literalinclude:: ../../../tutorials/AgileRL/requirements.txt
   :language: text
```

## Code
### Train multiple agents using MADDPG
The following code should run without any issues. The comments are designed to help you understand how to use PettingZoo with AgileRL. If you have any questions, please feel free to ask in the [Discord server](https://discord.com/invite/eB8HyTA2ux).

```{eval-rst}
.. literalinclude:: ../../../tutorials/AgileRL/agilerl_matd3.py
   :language: python
```

### Watch the trained agents play
The following code allows you to load your saved MATD3 alogorithm from the previous training block, test the algorithms performance, and then visualise a number of episodes as a gif.
```{eval-rst}
.. literalinclude:: ../../../tutorials/AgileRL/render_agilerl_matd3.py
   :language: python
```
