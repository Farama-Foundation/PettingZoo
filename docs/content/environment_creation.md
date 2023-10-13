---
title: Environment Creation
---
# Environment Creation

This documentation overviews creating new environments and relevant useful wrappers, utilities and tests included in PettingZoo designed for the creation of new environments.


We will walk through the creation of a simple Rock-Paper-Scissors environment, with example code for both [AEC](/api/aec/) and [Parallel](/api/parallel/) environments.

See our [Custom Environment Tutorial](/tutorials/custom_environment/index) for a full walkthrough on creating custom environments, including complex environment logic and illegal action masking.

## Example Custom Environment

This is a carefully commented version of the PettingZoo rock paper scissors environment.

```{eval-rst}
.. literalinclude:: ../code_examples/aec_rps.py
   :language: python
```

To interact with your custom AEC environment, use the following code:

```{eval-rst}
.. literalinclude:: ../code_examples/aec_rps_usage.py
   :language: python
```

## Example Custom Parallel Environment

```{eval-rst}
.. literalinclude:: ../code_examples/parallel_rps.py
   :language: python
```

To interact with your custom parallel environment, use the following code:

```{eval-rst}
.. literalinclude:: ../code_examples/parallel_rps_usage.py
   :language: python
```

## Using Wrappers

A wrapper is an environment transformation that takes in an environment as input, and outputs a new environment that is similar to the input environment, but with some transformation or validation applied. PettingZoo provides [wrappers to convert environments](/api/pz_wrappers) back and forth between the AEC API and the Parallel API and a set of simple [utility wrappers](/api/pz_wrappers) which provide input validation and other convenient reusable logic. PettingZoo also includes [wrappers](/api/supersuit_wrappers) via the SuperSuit companion package (`pip install supersuit`).

```python
from pettingzoo.butterfly import pistonball_v6
from pettingzoo.utils import ClipOutOfBoundsWrapper

env = pistonball_v6.env()
wrapped_env = ClipOutOfBoundsWrapper(env)
# Wrapped environments must be reset before use
wrapped_env.reset()
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
``` python notest
from pettingzoo.butterfly import knights_archers_zombies_v0
knights_archers_zombies_v0.env()
# pettingzoo.utils.deprecated_module.DeprecatedEnv: knights_archers_zombies_v0 is now deprecated, use knights_archers_zombies_v10 instead
```
