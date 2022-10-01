PettingZoo 2 is a Python library for conducting research in multi-agent reinforcement learning (MARL), 
akin to a multi-agent version of [Gymnasium](https://github.com/farama-Foundation/gymnasium).

```python
import pettingzoo as pz

env = pz.make("KnightArcherZombies-v10")
policies = {agent_name: policy, ...}

obs, info = env.reset(seed=10)
while env.active:
    actions = {agent_name: policies[agent_name](agent_obs) for agent_name, agent_obs in obs.items()}
    obs, rewards, terminations, truncations, info = env.step(actions)
env.close()
```

The API is very similar to Gymnasium with several key changes to the `reward`, `termination` and `env.active` parameters.

PettingZoo 2 is in a development stage, aiming to rewrite a module with a new API that can use a majority of the wrappers 
and API from Gymnasium.
