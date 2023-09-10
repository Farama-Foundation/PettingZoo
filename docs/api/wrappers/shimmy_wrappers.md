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

To load a DeepMind Control [multi-agent soccer game](https://github.com/deepmind/dm_control/blob/main/dm_control/locomotion/soccer/README.md):

```python notest
from shimmy import DmControlMultiAgentCompatibilityV0
from dm_control.locomotion import soccer as dm_soccer

env = dm_soccer.load(team_size=2)
env = DmControlMultiAgentCompatibilityV0(env, render_mode="human")

observations, infos = env.reset()
while env.agents:
    actions = {agent: env.action_space(agent).sample() for agent in env.agents}  # this is where you would insert your policy
    observations, rewards, terminations, truncations, infos = env.step(actions)
```


To load an OpenSpiel game of [backgammon](https://github.com/deepmind/open_spiel/blob/master/docs/games.md#backgammon), wrapped with [TerminateIllegalWrapper](https://pettingzoo.farama.org/api/wrappers/pz_wrappers/#pettingzoo.utils.wrappers.TerminateIllegalWrapper):
```python notest
from shimmy import OpenSpielCompatibilityV0
from pettingzoo.utils import TerminateIllegalWrapper

env = OpenSpielCompatibilityV0(game_name="chess", render_mode=None)
env = TerminateIllegalWrapper(env, illegal_reward=-1)

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


To load a Melting Pot [prisoner's dilemma in the matrix](https://github.com/deepmind/meltingpot/blob/main/docs/substrate_scenario_details.md#prisoners-dilemma-in-the-matrix) substrate:

```python notest
from shimmy import MeltingPotCompatibilityV0
env = MeltingPotCompatibilityV0(substrate_name="prisoners_dilemma_in_the_matrix__arena", render_mode="human")
observations, infos = env.reset()
while env.agents:
    actions = {agent: env.action_space(agent).sample() for agent in env.agents}
    observations, rewards, terminations, truncations, infos = env.step(actions)
    env.step(actions)
env.close()
```


For more information, see [Shimmy documentation](https://shimmy.farama.org).

## Multi-Agent Compatibility Wrappers:
```{eval-rst}
- :external:py:class:`shimmy.dm_control_multiagent_compatibility.DmControlMultiAgentCompatibilityV0`
- :external:py:class:`shimmy.openspiel_compatibility.OpenSpielCompatibilityV0`
- :external:py:class:`shimmy.meltingpot_compatibility.MeltingPotCompatibilityV0`
```

## Citation

If you use this in your research, please cite:

```
@software{shimmy2022github,
  author = {{Jun Jet Tai, Mark Towers, Elliot Tower} and Jordan Terry},
  title = {Shimmy: Gymnasium and PettingZoo Wrappers for Commonly Used Environments},
  url = {https://github.com/Farama-Foundation/Shimmy},
  version = {1.0.0},
  year = {2022},
}
```
