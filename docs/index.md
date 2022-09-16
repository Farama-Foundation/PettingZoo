---
hide-toc: true
firstpage:
lastpage:
---

```{toctree}
:hidden:
:caption: Introduction

content/basic_usage
```

```{toctree}
:hidden:
:caption: API

content/core
content/api
content/environment_creation
content/environment_tests
content/wrappers
cont   s
```

```{toctree}
:hidden:
:caption: Environments

environments/atari
environments/butterfly
environments/classic
environments/magent
environments/mpe
environments/sisl
environments/third_party_envs
```

```{toctree}
:hidden:
:caption: Tutorial
content/environment_creation
```

```{toctree}
:hidden:
:caption: Development

Github <https://github.com/Farama-Foundation/PettingZoo>
Donate <https://farama.org/donations>

```

<br>

```{figure} environments/atari/atari_warlords.gif
    :width: 160px
    :name: warlods
```

## Usage

Environments can be interacted with in a manner very similar to Gym:

```python
  from pettingzoo.butterfly import knights_archers_zombies_v10
  env = knights_archers_zombies_v10.env()
  env.reset()
  for agent in env.agent_iter():
      observation, reward, done, info = env.last()
      action = policy(observation, agent)
      env.step(action)
```