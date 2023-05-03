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

tutorials/environmentcreation/index
tutorials/cleanrl/index
tutorials/tianshou/index
tutorials/rllib/index
```

```{toctree}
:hidden:
:caption: Development

Github <https://github.com/Farama-Foundation/PettingZoo>
release_notes/index
Contribute to the Docs <https://github.com/Farama-Foundation/PettingZoo/tree/master/docs/>
```
<style>
h2 { 
    padding-top: 10px;
    padding-bottom: 20px;
    font-size: 29px;
    margin: 0;
    overflow: auto;
}
.logo{
  padding-left: 9%;
  vertical-align:bottom;
  padding-bottom: 0;
  padding-top: 10px;
}
</style>


<center>
    <div class="logo">
        <img src="_static/img/pettingzoo-text.png" width="65%" alt="PettingZoo Logo">
    </div>
    <h2>An API standard for multi-agent reinforcement learning</h2>
</center>

```{figure} _static/img/environments-demo.gif
    :width: 480px
    :name: PettingZoo environments
```

**PettingZoo is a simple, pythonic interface capable of representing general multi-agent reinforcement learning (MARL) problems.**
PettingZoo includes a wide variety of reference environments, helpful utilities, and tools for creating your own custom environments.

Environments can be interacted with using a similar interface to [Gymnasium](https://gymnasium.farama.org):

```python
  from pettingzoo.butterfly import knights_archers_zombies_v10
  env = knights_archers_zombies_v10.env(render_mode="human")
  env.reset(seed=42)
  for agent in env.agent_iter():
      observation, reward, termination, truncation, info = env.last()
      action = policy(observation, agent)
      env.step(action)
```
