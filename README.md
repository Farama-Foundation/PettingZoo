<p align="center">
    <img src="PettingZoo_Text.png" width="500px"/>
</p>

[![Build Status](https://github.com/PettingZoo-Team/PettingZoo/workflows/Python%20tests/badge.svg)](https://github.com/PettingZoo-Team/PettingZoo/actions?query=workflow%3A%22Python+tests%22)

PettingZoo is a Python library for conducting research in multi-agent reinforcement learning. It's akin to a multi-agent version of OpenAI's Gym library.

Our website, with comprehensive documentation, is [pettingzoo.ml](https://www.pettingzoo.ml)

## Environments and Installation

PettingZoo includes the following families of environments:

* [Atari](https://www.pettingzoo.ml/atari): Multi-player Atari 2600 games (both cooperative and competitive)
* [Butterfly](https://www.pettingzoo.ml/butterfly): Cooperative graphical games developed by us, requiring a high degree of coordination
* [Classic](https://www.pettingzoo.ml/classic): Classical games including card games, board games, etc.
* [MAgent](https://www.pettingzoo.ml/magent): Configurable environments with massive numbers of particle agents, originally from https://github.com/geek-ai/MAgent
* [MPE](https://www.pettingzoo.ml/mpe): A set of simple nongraphical communication tasks, originally from https://github.com/openai/multiagent-particle-envs
* [SISL](https://www.pettingzoo.ml/sisl): 3 cooperative environments, originally from https://github.com/sisl/MADRL

To install the pettingzoo base library, use `pip install pettingzoo`.

This does not include dependencies for all families of environments (there's a massive number, and some can be problematic to install on certain systems). You can install these dependencies for one family like `pip install pettingzoo[atari]` or use `pip install pettingzoo[all]` to install all dependencies.

We support Python 3.6, 3.7 and 3.8 on Linux and macOS.

## API

PettingZoo model environments as [*Agent Environment Cycle* (AEC) games](https://arxiv.org/abs/2009.13051), in order to be able to cleanly support all types of multi-agent RL environments under one API and to minimize the potential for certain classes of common bugs.

Using environments in PettingZoo is very similar to Gym, i.e. you initialize an environment via:

```
from pettingzoo.butterfly import pistonball_v3
env = pistonball_v3.env()
```

Environments can be interacted with in a manner very similar to Gym:

```
env.reset()
for agent in env.agent_iter():
    observation, reward, done, info = env.last()
    action = policy(observation)
    env.step(action)
```

For the complete API documentation, please see https://www.pettingzoo.ml/api

### Parallel API

In certain environments, it's a valid to assume that agents take their actions at the same time. For these games, we offer a secondary API to allow for parallel actions, documented at https://www.pettingzoo.ml/api#parallel-api

## SuperSuit

SuperSuit is a library that includes all commonly used wrappers in RL (frame stacking, observation, normalization, etc.) for PettingZoo and Gym environments with a nice API. We developed it in lieu of wrappers built into PettingZoo. https://github.com/PettingZoo-Team/SuperSuit

## Environment Versioning

PettingZoo keeps strict versioning for reproducibility reasons. All environments end in a suffix like "\_v0".  When changes are made to environments that might impact learning results, the number is increased by one to prevent potential confusion.

## Release History

Version 1.5.1 (January 5, 2021)

Fixes MPE rendering dependency, fixes minor left over dependencies on six, fixes issues when pickling Pistonball. No versions were bumped.

Version 1.5.0 (January 5, 2021)

Refactors tests to be generally usable by third party environments. Added average reward calculating util, and made minor improvements to random_demo and save_obs utils. Removed black death argument from KAZ (it's now a wrapper in supersuit). Redid how illegal actions are handled in classic, by making observations dictionaries where one element is the observation and the other is a proper illegal action mask. Pistonball was refactored for readability, to run faster and to allow the number of pistons to be varied via argument. Waterworld was completely refactored with various major fixes. RLCard version was bumped (and includes bug fixes impacting environments). MAgent rendering looks much better now (versions not bumped). Major bug in the observation space of pursuit is fixed. Add Python 3.9 support. Update Gym version. Fixed multiwalker observation space, for good this time, and made large improvements to code quality. Removed NaN wrapper. 

Version 1.4.2 (November 25, 2020)

Pistonball reward and miscellanious problems. Fixed KAZ observation and rendering issues. Fix Cooperative Pong issues with rendering. Fixed default parameters in Hanabi. Fixed multiwalker rewards, added arguments. Changed combined_arms observation and rewards, tiger_deer rewards. Added more arguments to all MAgent environments.

Version 1.4.0 (November 6, 2020)

General: Substantial API upgrades (see https://www.pettingzoo.ml/api), overhaul of the handling of agent death. In particular, the agents list now only contains live agents (agents which have not been done). Moved significant logic from wrappers to raw environment. Renamed max_frames to max_cycles and made the meaning of this argument consistent across all environments.

Atari: Fixed entombed_cooperative rewards, add support for custom ROM directory specification

Butterfly: Bug fixes in all environment, bumped PyGame and PyMunk versions

Classic: Bumped RLCard version, fixed default observation space for many environments depending on RLCard

SISL: Bug fixes in all environments

MAgent: Fixes to observation space of all environments

Bumped versions of all environments. There hopefully will be no more major API changes after this.

Version 1.3.5 (October 14, 2020)

Fixed numerous more prospector issues, added checkers, renamed Atari Pong based environments.

Version 1.3.4 (October 3, 2020)

Fixed prospector agents leaving game area, changed default max_iter of MPE environments to be the same as in original, fixed to_parallel wrapper issue which was causing crashes with rllib.

Version 1.3.3 (September 22, 2020)

Fixed observation issue multiwalker environment, fixed MPE speaker listener naming scheme, renamed max_agent_iter to max_iter.

Version 1.3.2 (September 17, 2020)

Fixed import issue for depreciated multiwalker environment.

Version 1.3.1 (September 16, 2020)

Various fixes and parameter changes for all SISL environments, bumped versions. Fixed dones computations in knights_archers_zombies and cooperative_pong, bumped versions. Fixed install extras.

Version 1.3.0 (September 8, 2020):

Fixed how agent iter wrapper handles premature agent death. Bumped environments with death (joust, mario_bros, maze_craze, warlords, wizard_of_wor, knights_archers_zombies, battle, battlefield, combined_arms, gather, tiger_deer, multiwalker). Also switched MAgent to having a native parallel environment, making it much faster. We bumped adverserial pursuit as well due to this.

Version 1.2.1 (August 31, 2020):

Fixed ability to indefinitely stall in Double Dunk, Othello, Tennis and Video Checkers Atari environments, bumped versions to v1.

Version 1.2.0 (August 27, 2020):

Large fix to quadrapong, version bumped to v1.

Version 1.1.0 (August 20, 2020):

Added [ParallelEnv](https://www.pettingzoo.ml/api#parallel-api) API where all agents step at once. Fixed entombed_competitive rewards and bumped environment version to entombed_competitive_v1. Fixed prospector rewards and bumped version to prospector_v1.

Version 1.0.1 (August 12, 2020):

Fixes to continuous mode on pistonball and prison butterfly environments, along with a bad test that let the problems slip through. Versions bumped on both games.

Version 1.0.0 (August 5th, 2020):

This is the first official stable release of PettingZoo. Any changes to environments after this point will result in incrementing the environment version number. We currently plan to do three more things for PettingZoo beyond general maintenance: write a paper and put it on Arxiv, add Shogi as a classic environment using python-shogi, and add "colosseum"- an online tool for benchmarking competitive environments.


## Citation

To cite this project in publication, please use

```
@article{terry2020pettingzoo,
  Title = {PettingZoo: Gym for Multi-Agent Reinforcement Learning},
  Author = {Terry, Justin K and Black, Benjamin and Jayakumar, Mario and Hari, Ananth and Santos, Luis and Dieffendahl, Clemens and Williams, Niall L and Lokesh, Yashas and Sullivan, Ryan and Horsch, Caroline and Ravi, Praveen},
  journal={arXiv preprint arXiv:2009.14471},
  year={2020}
}
```

## OS Support

We support Linux and macOS, and conduct CI testing on both. We will accept PRs related to Windows, but do not officially support it. We're open to help properly supporting Windows.

## Reward Program

We have a sort bug/documentation error bounty program, inspired by [Donald Knuth's reward checks](https://en.wikipedia.org/wiki/Knuth_reward_check). People who make mergable PRs which properly address meaningful problems in the code, or which make meaningful improvements to the documentation, can receive a negotiable check for "hexadecimal dollar" ($2.56) mailed to them, or sent to them via PayPal. To redeem this, just send an email to justinkterry@gmail.com with your mailing address or PayPal address. We also pay out 32 cents for small fixes. This reward extends to libraries maintained by the PettingZoo team that PettingZoo depends on.
