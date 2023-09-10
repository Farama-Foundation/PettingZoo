---
title: PettingZoo Wrappers
---

# PettingZoo Wrappers

PettingZoo includes the following types of wrappers:
* [Conversion Wrappers](#conversion-wrappers): wrappers for converting environments between the [AEC](/api/aec/) and [Parallel](/api/parallel/) APIs
* [Utility Wrappers](#utility-wrappers): a set of wrappers which provide convenient reusable logic, such as enforcing turn order or clipping out-of-bounds actions.

## Conversion wrappers

### AEC to Parallel

```{eval-rst}
.. currentmodule:: pettingzoo.utils.conversions

.. automodule:: pettingzoo.utils.conversions
   :members: aec_to_parallel
   :undoc-members:
```

An environment can be converted from an AEC environment to a parallel environment with the `aec_to_parallel` wrapper shown below. Note that this wrapper makes the following assumptions about the underlying environment:

1. The environment steps in a cycle, i.e. it steps through every live agent in order.
2. The environment does not update the observations of the agents except at the end of a cycle.

Most parallel environments in PettingZoo only allocate rewards at the end of a cycle. In these environments, the reward scheme of the AEC API an the parallel API is equivalent.  If an AEC environment does allocate rewards within a cycle, then the rewards will be allocated at different timesteps in the AEC environment an the Parallel environment. In particular, the AEC environment will allocate all rewards from one time the agent steps to the next time, while the Parallel environment will allocate all rewards from when the first agent stepped to the last agent stepped.

To convert an AEC environment into a parallel environment:
``` python
from pettingzoo.utils.conversions import aec_to_parallel
from pettingzoo.butterfly import pistonball_v6
env = pistonball_v6.env()
env = aec_to_parallel(env)
```

### Parallel to AEC

```{eval-rst}
.. currentmodule:: pettingzoo.utils.conversions

.. automodule:: pettingzoo.utils.conversions
   :members: parallel_to_aec
   :undoc-members:
```

Any parallel environment can be efficiently converted to an AEC environment with the `parallel_to_aec` wrapper.

To convert a parallel environment into an AEC environment:
``` python
from pettingzoo.utils import parallel_to_aec
from pettingzoo.butterfly import pistonball_v6
env = pistonball_v6.parallel_env()
env = parallel_to_aec(env)
```


## Utility Wrappers

We wanted our pettingzoo environments to be both easy to use and easy to implement. To combine these, we have a set of simple wrappers which provide input validation and other convenient reusable logic.

You can apply these wrappers to your environment in a similar manner to the below examples:

To wrap an AEC environment:
```python
from pettingzoo.utils import TerminateIllegalWrapper
from pettingzoo.classic import tictactoe_v3
env = tictactoe_v3.env()
env = TerminateIllegalWrapper(env, illegal_reward=-1)

env.reset()
for agent in env.agent_iter():
    observation, reward, termination, truncation, info = env.last()
    if termination or truncation:
        action = None
    else:
        action = env.action_space(agent).sample()  # this is where you would insert your policy
    env.step(action)
env.close()
```
Note: Most AEC environments include TerminateIllegalWrapper in their initialization, so this code does not change the environment's behavior.

To wrap a Parallel environment.
```python
from pettingzoo.utils import BaseParallelWrapper
from pettingzoo.butterfly import pistonball_v6

parallel_env = pistonball_v6.parallel_env(render_mode="human")
parallel_env = BaseParallelWrapper(parallel_env)

observations, infos = parallel_env.reset()

while parallel_env.agents:
    actions = {agent: parallel_env.action_space(agent).sample() for agent in parallel_env.agents}  # this is where you would insert your policy
    observations, rewards, terminations, truncations, infos = parallel_env.step(actions)
```

```{eval-rst}
.. warning::

    Included PettingZoo wrappers currently do not support parallel environments, to use them you must convert your environment to AEC, apply the wrapper, and convert back to parallel.
```
```python
from pettingzoo.utils import ClipOutOfBoundsWrapper
from pettingzoo.sisl import multiwalker_v9
from pettingzoo.utils import aec_to_parallel

parallel_env = multiwalker_v9.env(render_mode="human")
parallel_env = ClipOutOfBoundsWrapper(parallel_env)
parallel_env = aec_to_parallel(parallel_env)

observations, infos = parallel_env.reset()

while parallel_env.agents:
    actions = {agent: parallel_env.action_space(agent).sample() for agent in parallel_env.agents}  # this is where you would insert your policy
    observations, rewards, terminations, truncations, infos = parallel_env.step(actions)
```

```{eval-rst}
.. currentmodule:: pettingzoo.utils.wrappers

.. autoclass:: BaseWrapper
.. autoclass:: TerminateIllegalWrapper
.. autoclass:: CaptureStdoutWrapper
.. autoclass:: AssertOutOfBoundsWrapper
.. autoclass:: ClipOutOfBoundsWrapper
.. autoclass:: OrderEnforcingWrapper

```
