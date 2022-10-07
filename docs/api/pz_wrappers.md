# PettingZoo Wrappers

## Conversion wrappers

### AEC to Parallel

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

### Parallel to AEC

Any parallel environment can be efficiently converted to an AEC environment with the `from_parallel` wrapper.

``` python
from pettingzoo.utils import from_parallel
from pettingzoo.butterfly import pistonball_v6
env = pistonball_v6.parallel_env()
env = from_parallel(env)
```

## Utility Wrappers

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