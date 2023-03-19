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
[Cooperative Pong](https://pettingzoo.farama.org/environments/butterfly/cooperative_pong/),
[Knights Archers Zombies](https://pettingzoo.farama.org/environments/butterfly/knights_archers_zombies/),
[Pistonball](https://pettingzoo.farama.org/environments/butterfly/pistonball/).

### Installation 
The unique dependencies for this set of environments can be installed via:

````bash
pip install pettingzoo[butterfly]
````

### Usage

To launch a [Pistonball](https://pettingzoo.farama.org/environments/butterfly/pistonball/) environment with agents taking random actions:
``` python
from pettingzoo.butterfly import pistonball_v6
env = pistonball_v6.parallel_env(render_mode="human")

env.reset()
while env.agents:
    actions = {agent: env.action_space(agent).sample() for agent in env.possible_agents}
    observations, rewards, terminations, truncations, infos = env.step(actions)
    env.step(actions)
```

To launch a [Knights Archers Zombies](https://pettingzoo.farama.org/environments/butterfly/knights_archers_zombies/) environment with interactive user input (see [manual_policy.py](https://github.com/Farama-Foundation/PettingZoo/blob/master/pettingzoo/butterfly/knights_archers_zombies/manual_policy.py), controls are WASD and space):
``` python
import pygame
from pettingzoo.butterfly import knights_archers_zombies_v10

env = knights_archers_zombies_v10.env(render_mode="human")
env.reset()

clock = pygame.time.Clock()
manual_policy = knights_archers_zombies_v10.ManualPolicy(env)

for agent in env.agent_iter():
    clock.tick(env.metadata["render_fps"])

    observation, reward, termination, truncation, info = env.last()
    if agent == manual_policy.agent:
        action = manual_policy(observation, agent)
    else:
        action = env.action_space(agent).sample()

    env.step(action)
```

