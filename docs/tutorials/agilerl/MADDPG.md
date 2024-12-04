# AgileRL: Implementing MADDPG
This tutorial shows how to train an [MADDPG](https://agilerl.readthedocs.io/en/latest/api/algorithms/maddpg.html) agent on the [space invaders](https://pettingzoo.farama.org/environments/atari/space_invaders/) atari environment.

## What is MADDPG?
[MADDPG](https://agilerl.readthedocs.io/en/latest/api/algorithms/maddpg.html) (Multi-Agent Deep Deterministic Policy Gradients) extends the [DDPG](https://agilerl.readthedocs.io/en/latest/api/algorithms/ddpg.html) (Deep Deterministic Policy Gradients) algorithm to enable cooperative or competitive training of multiple agents in complex environments, enhancing the stability and convergence of the learning process through decentralized actor and centralized critic architectures. For further information on MADDPG, check out the AgileRL [documentation](https://agilerl.readthedocs.io/en/latest/api/algorithms/maddpg.html).

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
### Train agents using MADDPG
The following code should run without any issues. The comments are designed to help you understand how to use PettingZoo with AgileRL. If you have any questions, please feel free to ask in the [Discord server](https://discord.com/invite/eB8HyTA2ux).

```{eval-rst}
.. literalinclude:: ../../../tutorials/AgileRL/agilerl_maddpg.py
   :language: python
```

### Watch the trained agents play
The following code allows you to load your saved MADDPG alogorithm from the previous training block, test the algorithms performance, and then visualise a number of episodes as a gif.
```{eval-rst}
.. literalinclude:: ../../../tutorials/AgileRL/render_agilerl_maddpg.py
   :language: python
```
