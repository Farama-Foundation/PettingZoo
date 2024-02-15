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
:caption: API

api/aec
api/parallel
api/wrappers
api/utils
```

```{toctree}
:hidden:
:caption: Environments

environments/atari
environments/butterfly
environments/classic
environments/mpe
environments/sisl
environments/third_party_envs
```

```{toctree}
:hidden:
:caption: Tutorials

tutorials/custom_environment/index
tutorials/cleanrl/index
tutorials/tianshou/index
tutorials/rllib/index
tutorials/langchain/index
tutorials/sb3/index
tutorials/agilerl/index
```

```{toctree}
:hidden:
:caption: Development

Github <https://github.com/Farama-Foundation/PettingZoo>
release_notes/index
Contribute to the Docs <https://github.com/Farama-Foundation/PettingZoo/tree/master/docs/>
```

```{project-logo} _static/img/pettingzoo-text.png
:alt: PettingZoo Logo
```

```{project-heading}
An API standard for multi-agent reinforcement learning.
```

```{figure} _static/img/environments-demo.gif
    :width: 480px
    :name: PettingZoo environments
```

**PettingZoo is a simple, pythonic interface capable of representing general multi-agent reinforcement learning (MARL) problems.**
PettingZoo includes a wide variety of reference environments, helpful utilities, and tools for creating your own custom environments.

The [AEC API](/api/aec/) supports sequential turn based environments, while the [Parallel API](/api/parallel/) supports environments with simultaneous actions.

Environments can be interacted with using a similar interface to [Gymnasium](https://gymnasium.farama.org):

```python
from pettingzoo.butterfly import knights_archers_zombies_v10
env = knights_archers_zombies_v10.env(render_mode="human")
env.reset(seed=42)

for agent in env.agent_iter():
    observation, reward, termination, truncation, info = env.last()

    if termination or truncation:
        action = None
    else:
        # this is where you would insert your policy
        action = env.action_space(agent).sample()

    env.step(action)
```
