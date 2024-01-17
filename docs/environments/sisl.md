---
title: SISL Environments
firstpage:
---

# SISL

```{toctree}
:hidden:
sisl/multiwalker
sisl/pursuit
sisl/waterworld
```

```{raw} html
    :file: sisl/list.html
```

The SISL environments are a set of three cooperative multi-agent benchmark environments, created at SISL (Stanford Intelligent Systems Laboratory)) and released as part of "Cooperative multi-agent control using deep reinforcement learning." The code was originally released at: [https://github.com/sisl/MADRL](https://github.com/sisl/MADRL)

### Installation

The unique dependencies for this set of environments can be installed via:

````bash
pip install 'pettingzoo[sisl]'
````

### Usage
To launch a [Waterworld](/environments/sisl/waterworld/) environment with random agents:

```python
from pettingzoo.sisl import waterworld_v4
env = waterworld_v4.env(render_mode='human')

env.reset()
for agent in env.agent_iter():
    observation, reward, termination, truncation, info = env.last()

    if termination or truncation:
        action = None
    else:
        action = env.action_space(agent).sample() # this is where you would insert your policy

    env.step(action)
env.close()
```

Please note that we've made major bug fixes to all environments included. As such, we discourage directly comparing results on these environments to those in the original paper.

If you use these environments, please additionally cite:

```
@inproceedings{gupta2017cooperative,
  title={Cooperative multi-agent control using deep reinforcement learning},
  author={Gupta, Jayesh K and Egorov, Maxim and Kochenderfer, Mykel},
  booktitle={International Conference on Autonomous Agents and Multiagent Systems},
  pages={66--83},
  year={2017},
  organization={Springer}
}
```
