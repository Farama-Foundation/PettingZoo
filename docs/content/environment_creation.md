---
title: Environment Creation
---
# Environment Creation

This documentation overviews creating new environments and relevant useful wrappers, utilities and tests included in PettingZoo designed for the creation of new environments.

## Example Custom Environment

This is a carefully commented version of the PettingZoo rock paper scissors environment.

```{eval-rst}
.. literalinclude:: ../code_examples/aec_rps.py
   :language: python
```

## Example Custom Parallel Environment

```{eval-rst}
.. literalinclude:: ../code_examples/parallel_rps.py
   :language: python
```

## Wrappers

A wrapper is an environment transformation that takes in an environment as input, and outputs a new environment that is similar to the input environment, but with some transformation or validation applied.

### Conversion wrappers

As we provide both the AEC API and the Parallel API, we also provide wrappers to convert environments back and forth between the two APIs.

#### AEC to Parallel

An environment can be converted from an AEC environment to a parallel environment with the `to_parallel` wrapper shown below. Note that this wrapper makes the following assumptions about the underlying environment:

1. The environment steps in a cycle, i.e. it steps through every live agent in order.
2. The environment does not update the observations of the agents except at the end of a cycle.

Most parallel environments in PettingZoo only allocate rewards at the end of a cycle. In these environments, the reward scheme of the AEC API an the parallel API is equivalent.  If an AEC environment does allocate rewards within a cycle, then the rewards will be allocated at different timesteps in the AEC environment an the Parallel environment. In particular, the AEC environment will allocate all rewards from one time the agent steps to the next time, while the Parallel environment will allocate all rewards from when the first agent stepped to the last agent stepped.

``` python
from pettingzoo.utils import to_parallel
from pettingzoo.butterfly import pistonball_v6
env = pistonball_v6.env()
env = to_parallel(env)
```

#### Parallel to AEC

Any parallel environment can be efficiently converted to an AEC environment with the `from_parallel` wrapper.

``` python
from pettingzoo.utils import from_parallel
from pettingzoo.butterfly import pistonball_v6
env = pistonball_v6.parallel_env()
env = from_parallel(env)
```

### Utility Wrappers

We wanted our pettingzoo environments to be both easy to use and easy to implement. To combine these, we have a set of simple wrappers which provide input validation and other convenient reusable logic.

* `BaseWrapper`: All AECEnv wrappers should inherit from this base class
* `TerminateIllegalWrapper`: Handles illegal move logic for classic games
* `CaptureStdoutWrapper`: Takes an environment which prints to terminal, and gives it an `ansi` render mode where it captures the terminal output and returns it as a string instead.
* `AssertOutOfBoundsWrapper`: Asserts if the action given to step is outside of the action space. Applied in PettingZoo environments with discrete action spaces.
* `ClipOutOfBoundsWrapper`: Clips the input action to fit in the continuous action space (emitting a warning if it does so). Applied to continuous environments in pettingzoo.
* `OrderEnforcingWrapper`: Gives a sensible error message if function calls or attribute access are in a disallowed order, for example if step() is called before reset(), or the .dones attribute is accessed before reset(), or if seed() is called and then step() is used before reset() is called again (reset must be called after seed()). Applied to all PettingZoo environments.

You can apply these wrappers to your environment in a similar manner to the below example:

``` python
from pettingzoo.utils import OrderEnforcingWrapper
from pettingzoo.butterfly import pistonball_v6
env = pistonball_v6.env()
env = OrderEnforcingWrapper(env)
```

## Developer Utils

The utils directory contains a few functions which are helpful for debugging environments. These are documented in the API docs.

The utils directory also contain some classes which are only helpful for developing new environments. These are documented below.

### Agent selector

The `agent_selector` class steps through agents in a cycle

It can be used as follows to cycle through the list of agents:

```python
from pettingzoo.utils import agent_selector
agents = ["agent_1", "agent_2", "agent_3"]
selector = agent_selector(agents)
agent_selection = selector.reset()
# agent_selection will be "agent_1"
for i in range(100):
    agent_selection = selector.next()
    # will select "agent_2", "agent_3", "agent_1", "agent_2", "agent_3", ..."
```

### Deprecated Module

The DeprecatedModule is used in PettingZoo to help guide the user away from old obsolete environment versions and toward new ones. If you wish to create a similar versioning system, this may be helpful.

For example, when the user tries to import the `knights_archers_zombies_v0` environment, they import the following variable (defined in `pettingzoo/butterfly/__init__.py`):
``` python
from pettingzoo.utils.deprecated_module import DeprecatedModule
knights_archers_zombies_v0 = DeprecatedModule("knights_archers_zombies", "v0", "v10")
```
This declaration tells the user that `knights_archers_zombies_v0` is deprecated and `knights_archers_zombies_v10` should be used instead. In particular, it gives the following error:
``` python
from pettingzoo.butterfly import knights_archers_zombies_v0
knights_archers_zombies_v0.env()
# pettingzoo.utils.deprecated_module.DeprecatedEnv: knights_archers_zombies_v0 is now deprecated, use knights_archers_zombies_v10 instead
```
