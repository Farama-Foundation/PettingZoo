---
title: Shimmy Compatibility Wrappers
---

# Shimmy Compatibility Wrappers

The [Shimmy](https://shimmy.farama.org/) package (`pip install shimmy`) allows commonly used external reinforcement learning environments to be used with PettingZoo and Gymnasium.

## Supported multi-agent environments:

### [OpenSpiel](https://shimmy.farama.org/contents/open_spiel/)
* 70+ implementations of various board games

### [DeepMind Control Soccer](https://shimmy.farama.org/contents/dm_multi/)
* Multi-agent robotics environment where teams of agents compete in soccer.

### [DeepMind Melting Pot](https://github.com/deepmind/meltingpot)
* Suite of test scenarios for multi-agent reinforcement learning
* Assesses generalization to novel social situations:
  * familiar and unfamiliar individuals
  * social interactions: cooperation, competition, deception, reciprocation, trust, stubbornness
* 50+ substrates and 250+ test scenarios

## Usage

To load a DeepMind Control multi-agent soccer game:

```python
from shimmy import DmControlMultiAgentCompatibilityV0
from dm_control.locomotion import soccer as dm_soccer

env = dm_soccer.load(team_size=2)
env = DmControlMultiAgentCompatibilityV0(env, render_mode="human")

observations = env.reset()
while env.agents:
    actions = {agent: env.action_space(agent).sample() for agent in env.agents}  # this is where you would insert your policy
    observations, rewards, terminations, truncations, infos = env.step(actions)
```

To load an OpenSpiel game of [backgammon](https://github.com/deepmind/open_spiel/blob/master/docs/games.md#backgammon):
```python
from shimmy import OpenspielCompatibilityV0
import pyspiel

env = pyspiel.load_game("backgammon")
env = OpenspielCompatibilityV0(game=env, render_mode=None)

env.reset()
for agent in env.agent_iter():
    observation, reward, termination, truncation, info = env.last()
    if termination or truncation:
        action = None
    else:
        action = env.action_space(agent).sample(info["action_mask"])  # this is where you would insert your policy
    env.step(action)
    env.render()

```

## Citation

If you use this in your research, please cite:

```
@software{shimmy2022github,
  author = {{Jun Jet Tai, Mark Towers} and Elliot Tower and Jordan Terry},
  title = {Shimmy: Gymnasium and Pettingzoo Wrappers for Commonly Used Environments},
  url = {http://github.com/Farama-Foundation/Shimmy},
  version = {0.2.0},
  year = {2022},
}```
```
