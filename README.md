<p align="center">
    <img src="PettingZoo_Text.png" width="500px"/>
</p>

[![Build Status](https://travis-ci.com/PettingZoo-Team/PettingZoo.svg?branch=master)](https://travis-ci.com/PettingZoo-Team/PettingZoo)

PettingZoo is a Python library for conducting research in multi-agent reinforcement learning. It's akin to a multi-agent version of OpenAI's Gym library.

We model environments as *Agent Environment Cycle* (AEC) games, in order to be able to support all types of multi-agent RL environments under one API.

Our website with comprehensive documentation is https://pettingzoo-team.github.io/PettingZoo/

## Environment Types and Installation

PettingZoo includes the following sets of games:

* [Atari](https://pettingzoo-team.github.io/PettingZoo/atari): Multi-player Atari 2600 games (both cooperative and competitive)
* [Butterfly](https://pettingzoo-team.github.io/PettingZoo/butterfly): Cooperative graphical games developed by us, requiring a high degree of coordination
* [Classic](https://pettingzoo-team.github.io/PettingZoo/classic): Classical games including card games, board games, etc.
* [MAgent](https://pettingzoo-team.github.io/PettingZoo/magent): Configurable environments with massive numbers of particle agents, originally from https://github.com/geek-ai/MAgent
* [MPE](https://pettingzoo-team.github.io/PettingZoo/mpe): A set of simple nongraphical communication tasks, originally from https://github.com/openai/multiagent-particle-envs
* [SISL](https://pettingzoo-team.github.io/PettingZoo/sisl): 3 cooperative environments, originally from https://github.com/sisl/MADRL

To install, use `pip install pettingzoo`

We support Python 3.6, 3.7 and 3.8, on Linux and macOS.

## API

Using environments in PettingZoo is very similar to Gym, i.e. you initialize an environment via:

```
from pettingzoo.butterfly import pistonball_v0
env = pistonball_v0.env()
```

Environments can be interacted with in a manner very similar to Gym:

```
observation = env.reset()
for agent in env.agent_iter():
    reward, done, info = env.last()
    action = policy(observation)
    observation = env.step(action)
```

For the complete API documentation, please see https://pettingzoo-team.github.io/PettingZoo/api

## Citation

To cite this project in publication, please use

```
@misc{pettingZoo2020,
  author = {Terry, Justin K and Black, Benjamin and Jayakumar, Mario  and Hari, Ananth and Santos, Luis and Dieffendahl, Clemens and Williams, Niall and Ravi, Praveen and Lokesh, Yashas and Horsch, Caroline and Patel, Dipam},
  title = {Petting{Z}oo},
  year = {2020},
  publisher = {GitHub},
  note = {GitHub repository},
  howpublished = {\url{https://github.com/PettingZoo-Team/PettingZoo}}
}
```

## OS Support

We support Linux and macOS, and conduct CI testing on both. We will accept PRs related to Windows, but do not officially support it. We're open to help properly supporting Windows.

## Reward Program

We have a sort bug/documentation error bounty program, inspired by [Donald Knuth's reward checks](https://en.wikipedia.org/wiki/Knuth_reward_check). People who make mergable PRs which properly address meaningful problems in the code, or which make meaningful improvements to the documentation, can receive a negotiable check for "hexadecimal dollar" ($2.56) mailed to them, or sent to them via PayPal. To redeem this, just send an email to justinkterry@gmail.com with your mailing address or PayPal address. We also pay out 32 cents for small fixes. This reward extends to libraries maintained by the PettingZoo team that PettingZoo depends on.
