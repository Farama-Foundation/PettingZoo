---
hide-toc: true
firstpage:
lastpage:
---

```{toctree}
:hidden:
:caption: Introduction

content/basic_usage
content/environment_creation
content/environment_tests
```

```{toctree}
:hidden:
:caption: Tutorials

tutorials/cleanrl/implementing_PPO
tutorials/tianshou/beginner
tutorials/tianshou/intermediate
tutorials/tianshou/advanced
tutorials/rllib/holdem
tutorials/rllib/pistonball
```

```{toctree}
:hidden:
:caption: API

api/core
api/parallel
api/pz_wrappers
api/supersuit_wrappers
api/utils
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
:caption: Development

Github <https://github.com/Farama-Foundation/PettingZoo>
Donate <https://farama.org/donations>

```

# PettingZoo is a Python library for conducting research in multi-agent reinforcement learning

```{figure} environments/atari/atari_warlords.gif
    :width: 230px
    :name: warlods
```

**Environments can be interacted with in a manner very similar to Gym:**

```python
  from pettingzoo.butterfly import knights_archers_zombies_v10
  env = knights_archers_zombies_v10.env()
  env.reset()
  for agent in env.agent_iter():
      observation, reward, termination, truncation, info = env.last()
      action = policy(observation, agent)
      env.step(action)
```
