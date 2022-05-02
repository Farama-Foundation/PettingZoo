---
layout: "contents"
title: Environment Creation
---
# Environment Creation

This documentation overviews creating new environments and relevant useful wrappers, utilities and tests included in PettingZoo designed for the creation of new environments.

## Example Custom Environment

This is a carefully commented version of the PettingZoo rock paper scissors environment.

```python
{% include code/aec_rps.py %}
```

## Example Custom Parallel Environment

```python
{% include code/parallel_rps.py %}
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

For example, when the user tries to import the `prospector_v0` environment, they import the following variable (defined in `pettingzoo/butterfly/__init__.py`):
``` python
from pettingzoo.utils.deprecated_module import DeprecatedModule
prospector_v0 = DeprecatedModule("prospector", "v0", "v3")
```
This declaration tells the user that `prospector_v0` is deprecated and `prospector_v4` should be used instead. In particular, it gives the following error:
``` python
from pettingzoo.butterfly import prospector_v0
prospector_v0.env()
# pettingzoo.utils.deprecated_module.DeprecatedEnv: prospector_v0 is now deprecated, use prospector_v4 instead
```

## Tests

PettingZoo has a number of compliance tests for environments through. If you are adding a new environment, we encourage you to run these tests on your own environment.

### API Test

PettingZoo's API has a number of features and requirements. To make sure your environment is consistent with the API, we have the api_test. Below is an example:

``` python
from pettingzoo.test import api_test
from pettingzoo.butterfly import pistonball_v6
env = pistonball_v6.env()
api_test(env, num_cycles=1000, verbose_progress=False)
```

As you can tell, you simply pass an environment to the test. The test will assert or give some other error on an API issue, and will return normally if it passes.

The optional arguments are:

*  `num_cycles`: runs the environment for that many cycles and checks that the output is consistent with the API.
* `verbose_progress`: Prints out messages to indicate partial completion of the test. Useful for debugging environments.

### Parallel API Test

This is an analogous version of the API test, but for parallel environments. You can use this test like:

``` python
from pettingzoo.test import parallel_api_test
from pettingzoo.butterfly import pistonball_v6
env = pistonball_v6.parallel_env()
parallel_api_test(env, num_cycles=1000)
```

### Seed Test

To have a properly reproducible environment that utilizes randomness, you need to be able to make it deterministic during evaluation by setting a seed for the random number generator that defines the random behavior. The seed test checks that calling the `seed()` method with a constant actually makes the environment deterministic.

The seed test takes in a function that creates a pettingzoo environment. For example

``` python
from pettingzoo.test import seed_test, parallel_seed_test
from pettingzoo.butterfly import pistonball_v6
env_fn = pistonball_v6.env
seed_test(env_fn, num_cycles=10, test_kept_state=True)

# or for parallel environments
parallel_env_fn = pistonball_v6.parallel_env
parallel_seed_test(parallel_env_fn, num_cycles=10, test_kept_state=True)
```

Internally, there are two separate tests.

1. Do two separate environments give the same result after the environment is seeded?
2. Does a single environment give the same result after seed() then reset() is called?

The first optional argument, `num_cycles`, indicates how long the environment will be run to check for determinism. Some environments only fail the test long after initialization.

The second optional argument, `test_kept_state` allows the user to disable the second test. Some physics based environments fail this test due to barely detectable differences due to caches, etc, which are not important enough to matter.

### Max Cycles Test

The max cycles test tests that the `max_cycles` environment argument exists and the resulting environment actually runs for the correct number of cycles. If your environment does not take a `max_cycles` argument, you should not run this test. The reason this test exists is that many off-by-one errors are possible when implementing `max_cycles`. An example test usage looks like:

``` python
from pettingzoo.test import max_cycles_test
from pettingzoo.butterfly import pistonball_v6
env = pistonball_v6.env()
max_cycles_test(env)
```

### Render Test

The render test checks that rendering 1) does not crash and 2) produces output of the correct type when given a mode (only supports `'human'`, `'ansi'`, and `'rgb_array'` modes).

``` python
from pettingzoo.test import render_test
from pettingzoo.butterfly import pistonball_v6
env = pistonball_v6.env()
render_test(env)
```

The render test method takes in an optional argument `custom_tests` that allows for additional tests in non-standard modes.

``` python
custom_tests = {
    "svg": lambda render_result: return isinstance(render_result, str)
}
render_test(env, custom_tests=custom_tests)
```

### Performance Benchmark Test

To make sure we do not have performance regressions, we have the performance benchmark test. This test simply prints out the number of steps and cycles that the environment takes in 5 seconds. This test requires manual inspection of its outputs:

``` python
from pettingzoo.test import performance_benchmark
from pettingzoo.butterfly import pistonball_v6
env = pistonball_v6.env()
performance_benchmark(env)
```

### Save Observation Test

The save observation test is to visually inspect the observations of games with graphical observations to make sure they are what is intended. We have found that observations are a huge source of bugs in environments, so it is good to manually check them when possible. This test just tries to save the observations of all the agents. If it fails, then it just prints a warning. The output needs to be visually inspected for correctness.

``` python
from pettingzoo.test import test_save_obs
from pettingzoo.butterfly import pistonball_v6
env = pistonball_v6.env()
test_save_obs(env)
```
