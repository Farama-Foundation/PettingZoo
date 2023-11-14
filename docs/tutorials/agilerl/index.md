# AgileRL Tutorial

These tutorials provide an introductory guide to using [AgileRL](https://github.com/AgileRL/AgileRL) with PettingZoo. AgileRL's multi-agent algorithms make use of the PettingZoo parallel API and allow users to train multiple-agents in parallel in both competitive and co-operative environments. This tutorial includes the following:

* [DQN](DQN.md): _Train a DQN agent to play Connect Four through curriculum learning and self-play_
* [MADDPG](MADDPG.md): _Train an MADDPG agent to play multi-agent atari games_
* [MATD3](MATD3.md): _Train an MATD3 agent to play multi-particle-environment games_

## AgileRL Overview

AgileRL is a deep reinforcement learning framework focused on streamlining training for reinforcement learning models. Using [evolutionary hyper-parameter optimisation](https://agilerl.readthedocs.io/en/latest/api/hpo/index.html) (HPO), AgileRL allows users to train models significantly faster and more accurately when compared with traditional HPO techniques. AgileRL's multi-agent algorithms orchestrate the training of multiple agents at the same time, and benchmarking has shown up to 4x increase in return in a shorter time-frame when compared with implementations of the very same algorithms in other reinforcement learning libraries.

For more information about AgileRL and what else the library has to offer, check out the [documentation](https://agilerl.readthedocs.io/en/latest/) and [GitHub repo](https://github.com/agilerl/agilerl).

## Examples using PettingZoo

* [MADDPG for co-operation: simple speaker listener environment](https://agilerl.readthedocs.io/en/latest/multi_agent_training/index.html)


```{eval-rst}
.. figure:: test_looped.gif
   :align: center
   :height: 400px

   Fig1: Performance of trained MADDPG algorithm on 6 random episodes
```

```{toctree}
:hidden:
:caption: AgileRL

DQN
MADDPG
MATD3
```
