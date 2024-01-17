---
title: Butterfly Environments
firstpage:
---

# Butterfly

```{toctree}
:hidden:
butterfly/cooperative_pong
butterfly/knights_archers_zombies
butterfly/pistonball
```

```{raw} html
    :file: butterfly/list.html
```

Butterfly environments are challenging scenarios created by Farama, using Pygame with visual Atari spaces.

All environments require a high degree of coordination and require learning of emergent behaviors to achieve an optimal policy. As such, these environments are currently very challenging to learn.

Environments are highly configurable via arguments specified in their respective documentation:
[Cooperative Pong](/environments/butterfly/cooperative_pong/),
[Knights Archers Zombies](/environments/butterfly/knights_archers_zombies/),
[Pistonball](/environments/butterfly/pistonball/).

### Installation
The unique dependencies for this set of environments can be installed via:

````bash
pip install 'pettingzoo[butterfly]'
````

### Usage

To launch a [Pistonball](/environments/butterfly/pistonball/) environment with random agents:
```python
from pettingzoo.butterfly import pistonball_v6

env = pistonball_v6.parallel_env(render_mode="human")
observations, infos = env.reset()

while env.agents:
    # this is where you would insert your policy
    actions = {agent: env.action_space(agent).sample() for agent in env.agents}

    observations, rewards, terminations, truncations, infos = env.step(actions)
env.close()
```

To launch a [Knights Archers Zombies](/environments/butterfly/knights_archers_zombies/) environment with interactive user input (see [manual_policy.py](https://github.com/Farama-Foundation/PettingZoo/blob/master/pettingzoo/butterfly/knights_archers_zombies/manual_policy.py)):
```python
import pygame
from pettingzoo.butterfly import knights_archers_zombies_v10

env = knights_archers_zombies_v10.env(render_mode="human")
env.reset(seed=42)

manual_policy = knights_archers_zombies_v10.ManualPolicy(env)

for agent in env.agent_iter():
    observation, reward, termination, truncation, info = env.last()

    if termination or truncation:
        action = None
    elif agent == manual_policy.agent:
        # get user input (controls are WASD and space)
        action = manual_policy(observation, agent)
    else:
        # this is where you would insert your policy (for non-player agents)
        action = env.action_space(agent).sample()

    env.step(action)
env.close()
```
