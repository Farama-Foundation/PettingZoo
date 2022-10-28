<p align="center">
    <img src="https://raw.githubusercontent.com/Farama-Foundation/PettingZoo/master/pettingzoo-text.png" width="500px"/>
</p>

PettingZoo is a Python library for conducting research in multi-agent reinforcement learning, akin to a multi-agent version of [Gymnasium](https://github.com/Farama-Foundation/Gymnasium).

The documentation website is at [pettingzoo.farama.org](https://pettingzoo.farama.org) and we have a public discord server (which we also use to coordinate development work) that you can join here: https://discord.gg/nhvKkYa6qX

## Environments

PettingZoo includes the following families of environments:

* [Atari](https://pettingzoo.farama.org/environments/atari/): Multi-player Atari 2600 games (cooperative, competitive and mixed sum)
* [Butterfly](https://pettingzoo.farama.org/environments/butterfly): Cooperative graphical games developed by us, requiring a high degree of coordination
* [Classic](https://pettingzoo.farama.org/environments/classic): Classical games including card games, board games, etc.
* [MPE](https://pettingzoo.farama.org/environments/mpe): A set of simple nongraphical communication tasks, originally from https://github.com/openai/multiagent-particle-envs
* [SISL](https://pettingzoo.farama.org/environments/sisl): 3 cooperative environments, originally from https://github.com/sisl/MADRL

## Installation

To install the pettingzoo base library, use `pip install pettingzoo`

This does not include dependencies for all families of environments (there's a massive number, and some can be problematic to install on certain systems). You can install these dependencies for one family like `pip install pettingzoo[atari]` or use `pip install pettingzoo[all]` to install all dependencies.

We support Python 3.7, 3.8, 3.9 and 3.10 on Linux and macOS. We will accept PRs related to Windows, but do not officially support it.

## Getting started

Get started with PettingZoo by following [the PettingZoo tutorial](https://pettingzoo.farama.org/tutorials/cleanrl/implementing_PPO/), where you'll train multiple PPO agents in the Pistonball environment using PettingZoo.

## API

PettingZoo model environments as [*Agent Environment Cycle* (AEC) games](https://arxiv.org/pdf/2009.14471.pdf), in order to be able to cleanly support all types of multi-agent RL environments under one API and to minimize the potential for certain classes of common bugs.

Using environments in PettingZoo is very similar to Gymnasium, i.e. you initialize an environment via:

```python
from pettingzoo.butterfly import pistonball_v6
env = pistonball_v6.env()
```

Environments can be interacted with in a manner very similar to Gymnasium:

```python
env.reset()
for agent in env.agent_iter():
    observation, reward, termination, truncation, info = env.last()
    action = None if termination or truncation else env.action_space(agent).sample()  # this is where you would insert your policy
    env.step(action)
```

For the complete API documentation, please see https://pettingzoo.farama.org/api/aec/

### Parallel API

In certain environments, it's a valid to assume that agents take their actions at the same time. For these games, we offer a secondary API to allow for parallel actions, documented at https://pettingzoo.farama.org/api/parallel/

## SuperSuit

SuperSuit is a library that includes all commonly used wrappers in RL (frame stacking, observation, normalization, etc.) for PettingZoo and Gymnasium environments with a nice API. We developed it in lieu of wrappers built into PettingZoo. https://github.com/Farama-Foundation/SuperSuit

## Environment Versioning

PettingZoo keeps strict versioning for reproducibility reasons. All environments end in a suffix like "\_v0".  When changes are made to environments that might impact learning results, the number is increased by one to prevent potential confusion.

## Citation

To cite this project in publication, please use

```
@article{terry2020pettingzoo,
  Title = {PettingZoo: Gym for Multi-Agent Reinforcement Learning},
  Author = {Terry, J. K and Black, Benjamin and Grammel, Nathaniel and Jayakumar, Mario and Hari, Ananth and Sulivan, Ryan and Santos, Luis and Perez, Rodrigo and Horsch, Caroline and Dieffendahl, Clemens and Williams, Niall L and Lokesh, Yashas and Sullivan, Ryan and Ravi, Praveen},
  journal={arXiv preprint arXiv:2009.14471},
  year={2020}
}
```
