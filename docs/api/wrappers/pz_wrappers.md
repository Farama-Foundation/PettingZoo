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
```python
from pettingzoo import make
from pettingzoo.utils.conversions import aec_to_parallel

env = make("aec", "butterfly/pistonball-v6")
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
```python
from pettingzoo import make
from pettingzoo.utils import parallel_to_aec

env = make("parallel", "butterfly/pistonball-v6")
env = parallel_to_aec(env)
```


## Utility Wrappers

We wanted our pettingzoo environments to be both easy to use and easy to implement. To combine these, we have a set of simple wrappers which provide input validation and other convenient reusable logic.

You can apply these wrappers to your environment in a similar manner to the below examples:

To wrap an AEC environment:
```python
from pettingzoo import make
from pettingzoo.utils import TerminateIllegalWrapper

env = make("aec", "classic/tictactoe-v3")
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
from pettingzoo import make
from pettingzoo.utils import BaseParallelWrapper

parallel_env = make("parallel", "butterfly/pistonball-v6", render_mode="human")
parallel_env = BaseParallelWrapper(parallel_env)

observations, infos = parallel_env.reset()

while parallel_env.agents:
    actions = {agent: parallel_env.action_space(agent).sample() for agent in parallel_env.agents}  # this is where you would insert your policy
    observations, rewards, terminations, truncations, infos = parallel_env.step(actions)
```

```{eval-rst}
.. note::

    Wrappers are specific to either the AEC or Parallel API unless documented
    otherwise. Parallel variants include ``Parallel`` in their name, such as
    :class:`AgentIndicatorParallelV1`. To apply an AEC-only wrapper to a Parallel
    environment, convert it to AEC, apply the wrapper, and convert it back.
```

`ClipOutOfBoundsWrapper` supports both APIs through the same constructor. It clips
each Parallel agent's action to that agent's Box bounds and preserves the
environment's reset and step return values.

```python
from pettingzoo import make
from pettingzoo.utils import ClipOutOfBoundsWrapper

parallel_env = make("parallel", "sisl/multiwalker-v9", render_mode="human")
parallel_env = ClipOutOfBoundsWrapper(parallel_env)

observations, infos = parallel_env.reset()

while parallel_env.agents:
    actions = {agent: parallel_env.action_space(agent).sample() for agent in parallel_env.agents}  # this is where you would insert your policy
    observations, rewards, terminations, truncations, infos = parallel_env.step(actions)
```

BlackDeathParallelV4 keeps the agents present at reset visible until the underlying episode finishes. After an agent leaves, later steps use a zero observation, zero reward, and empty info for that agent, and actions for it are ignored. Early termination/truncation flags are held back while the wrapped agent set remains active; on the final step, each agent's original termination versus truncation cause is reported. Environments that add new agents after reset are not supported.

### Replacing NaN actions with a no-op

`NanNoopV1` (AEC) and `NanNoopParallelV1` (Parallel) replace numeric actions containing a NaN with a caller-supplied no-op and emit a warning. They use the same no-op value for every agent, so choose a value that belongs to each affected agent's action space. The wrapper checks known agents when constructed and checks the affected agent again before replacing an action. Incompatible no-ops raise `ValueError`; replacements are copied so mutable arrays are not shared between agents or steps.

For example, action `1` means stay still in discrete Pistonball:

```python
import numpy as np
from pettingzoo import make
from pettingzoo.utils.wrappers import NanNoopParallelV1

env = NanNoopParallelV1(
    make("parallel", "butterfly/pistonball-v6", continuous=False),
    no_op_action=1,
)
observations, infos = env.reset(seed=42)
actions = dict.fromkeys(env.agents, 1)
actions[env.agents[0]] = np.nan
observations, rewards, terminations, truncations, infos = env.step(actions)
env.close()
```

For an AEC environment, use `NanNoopV1(env, no_op_action=...)`. Its `step(None)` for a dead agent is passed through unchanged. Both wrappers preserve actions without NaNs, even if they are otherwise invalid: they do not clip actions or choose a legal action from an action mask. Action and observation spaces are unchanged.

These classes replace SuperSuit's `nan_noop_v0` for the respective PettingZoo APIs. Supply the no-op when constructing the wrapper, then call `step` normally.

### Replacing NaN actions with a random action

`NanRandomV1` (AEC) and `NanRandomParallelV1` (Parallel) replace numeric actions containing a NaN with a random action from the acting agent's own action space and emit a warning. If the agent has an `action_mask`, in its dictionary observation or otherwise in its info, the replacement is drawn only from the actions the mask allows. Masks are supported for `Discrete` action spaces; a mask with the wrong shape, values other than 0 and 1, or no allowed action raises `ValueError`. Replacements come from the wrapper's own RNG, which `reset(seed=...)` reseeds, so seeded runs are reproducible.

For example, every NaN below becomes a random legal Connect Four move:

```python
import numpy as np
from pettingzoo import make
from pettingzoo.utils.wrappers import NanRandomV1

env = NanRandomV1(make("aec", "classic/connect_four-v3"))
env.reset(seed=42)
for agent in env.agent_iter():
    observation, reward, termination, truncation, info = env.last()
    env.step(None if termination or truncation else np.nan)
env.close()
```

Actions without NaNs pass through unchanged, even if the mask forbids them, and `step(None)` for a dead AEC agent is passed through. Action and observation spaces are unchanged. These classes replace SuperSuit's `nan_random_v0`, which looked for the mask under the key `"action mask"` and so ignored PettingZoo's `action_mask`.

### Repeating actions for several steps

`FrameSkipV1` (AEC) and `FrameSkipParallelV1` (Parallel) use each action for `num_frames` steps of the wrapped environment. Rewards from those steps are added up. The observation, termination, truncation and info are the latest ones from the wrapped environment, and stepping stops early when the episode ends.

```python
from pettingzoo import make
from pettingzoo.utils.wrappers import FrameSkipParallelV1

env = FrameSkipParallelV1(
    make("parallel", "butterfly/pistonball-v6", continuous=False), num_frames=4
)
observations, infos = env.reset(seed=42)
while env.agents:
    actions = {agent: env.action_space(agent).sample() for agent in env.agents}
    observations, rewards, terminations, truncations, infos = env.step(actions)
env.close()
```

`FrameSkipParallelV1` also accepts a range `num_frames=(low, high)`. The number of steps is then drawn on every call from the `np_random` generator of `env.unwrapped`, which the environment seeds on `reset(seed=...)`. Agents added partway through a call use `default_action` until the next call, and a `ValueError` is raised if none was given.

`FrameSkipV1` takes a fixed `num_frames` only. An agent's action is replayed on its next `num_frames - 1` turns, and the caller is asked for an action whenever the wrapped environment selects an agent with nothing left to replay, so the turn order is unchanged. `last()` reports the rewards the agent collected since it last acted. Agents that finish during replaying still get their `step(None)` from the caller.

These classes replace SuperSuit's `frame_skip_v0` for the respective PettingZoo APIs.

```{eval-rst}
.. currentmodule:: pettingzoo.utils.wrappers

.. autoclass:: BaseWrapper
.. autoclass:: BlackDeathParallelV4
.. autoclass:: TerminateIllegalWrapper
.. autoclass:: CaptureStdoutWrapper
.. autoclass:: AssertOutOfBoundsWrapper
.. autoclass:: ClipOutOfBoundsWrapper
.. autoclass:: ClipRewardV1
.. autoclass:: ClipRewardParallelV1
.. autoclass:: OrderEnforcingWrapper
.. autoclass:: NanNoopV1
.. autoclass:: NanNoopParallelV1
.. autoclass:: NanRandomV1
.. autoclass:: NanRandomParallelV1
.. autoclass:: NanZerosV1
.. autoclass:: NanZerosParallelV1
.. autoclass:: AgentIndicatorV1
.. autoclass:: AgentIndicatorParallelV1
.. autoclass:: ColorReductionObservationV1
.. autoclass:: ColorReductionObservationParallelV1
.. autoclass:: DtypeObservationV1
.. autoclass:: DtypeObservationParallelV1
.. autoclass:: FlattenObservation
.. autoclass:: FlattenObservationParallel
.. autoclass:: FrameSkipV1
.. autoclass:: FrameSkipParallelV1
.. autoclass:: FrameStackV3
.. autoclass:: MaxObservationV1
.. autoclass:: MaxObservationParallelV1
.. autoclass:: PadActionSpaceV1
.. autoclass:: PadActionSpaceParallelV1
.. autoclass:: PadObservationsV1
.. autoclass:: PadObservationsParallelV1
.. autoclass:: RescaleObservationV1
.. autoclass:: RescaleObservationParallelV1
.. autoclass:: ReshapeObservationV1
.. autoclass:: ReshapeObservationParallelV1
.. autoclass:: ScaleActionV1
.. autoclass:: ScaleActionParallelV1
.. autoclass:: StickyActionV1
.. autoclass:: StickyActionParallelV1

```
