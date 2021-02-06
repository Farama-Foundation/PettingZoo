
# Example custom environment



# Utility wrappers

We wanted our pettingzoo environments to be both easy to use and easy to implement. To combine these, we have a set of simple wrappers which provide input validation and other convenient reusable logic.

* `BaseWrapper`: all AECEnv wrappers should inherit from this base class
* `TerminateIllegalWrapper`: which handles illegal move logic for classic games
* `CaptureStdoutWrapper`: which takes an environment which prints to terminal, and gives it an `ansi` render mode where it captures the terminal output and returns it as a string instead.
* `AssertOutOfBoundsWrapper`: Asserts if the action given to step is outside of the action space. Applied in PettingZoo environments with discrete action spaces.
* `ClipOutOfBoundsWrapper`: Clips the input action to fit in the continuous action space (emitting a warning if it does so). Applied to continuous environments in pettingzoo.
* `OrderEnforcingWrapper`: Gives a sensible error message if function calls or attribute access are in a disallowed order, for example if step() is called before reset(), or .dones attribute is accessed before reset(), or if seed() and then step() is called before reset() is called again (reset must be called after seed()). Applied to all PettingZoo environments.


# Utils

### Average Total Reward Util

The average total reward for an environment, as presented in the documentation, is summed over all agents over all steps in the episode, averaged over episodes.

This value is important for establishing the simplest possible baseline: the random policy.

```
from pettingzoo.utils import average_total_reward
from pettingzoo.butterfly import pistonball_v3
env = pistonball_v3.env()
average_total_reward(env, max_episodes=100, max_steps=10000000000)
```

Where `max_episodes` and `max_stpes` both limit the total number of evaluations (when the first is hit evaluation stops)

### Manual Control

Often, you want to be able to play before trying to learn it to get a better feel for it. Some of our games directly support this:

```python
from pettingzoo.butterfly import prison_v2
prison_v2.manual_control(<environment parameters>)
```

Environments say if they support this functionality in their documentation, and what the specific controls are.

### Random Demo

You can also easily get a quick impression of them by watching a random policy control all the actions:

```python
from pettingzoo.utils import random_demo
random_demo(env, render=True, cycles=100000000)
```

### Observation Saving

If the agents in a game make observations that are images then the observations can be saved to an image file. This function takes in the environment, along with a specified agent. If no `agent` is specified, then the current selected agent for the environment is chosen. If `all_agents` is passed in as `True`, then the observations of all agents in the environment is saved. By default, the images are saved to the current working directory in a folder matching the environment name. The saved image will match the name of the observing agent. If `save_dir` is passed in, a new folder is created where images will be saved to. This function can be called during training/evaluation if desired, which is why environments have to be reset before it can be used.

```python
from pettingzoo.utils import save_observation
from pettingzoo.butterfly import pistonball_v3
env = pistonball_v3.env()
env.reset()
save_observation(env, agent=None, all_agents=False, save_dir=os.getcwd())
```



# Tests

PettingZoo has a number of tests which it puts environments through. If you are adding a new environment, we encourage you to run these tests on your own environment.

### API test

PettingZoo's API has a number of features and requirements. To make sure your environment is consistent with the API, we have the api_test. Below is an example:

```
from pettingzoo.test import api_test
from pettingzoo.butterfly import pistonball_v3
env = pistonball_v3.env()
api_test(env, num_cycles=10, verbose_progress=False)
```

As you can tell, you simply pass an environment to the test. The test will assert or give some other error on an API issue, and will return normally if it passes.

The optional arguments are:

*  `num_cycles`: runs the environment for that many cycles and checks that the output is consistent with the API.
* `verbose_progress`: Prints out messages to indicate partial completion of the test. Useful for debugging environments.

### Parallel Play test

This is an analogous version of the API test, but for parallel environments. You can use this environment like:

```
from pettingzoo.test import parallel_play_test
from pettingzoo.butterfly import pistonball_v3
env = pistonball_v3.parallel_env()
parallel_play_test(env, num_cycles=10)
```

### Seed Test

To have a properly reproducible environment that utilizes randomness, you need to be able to make it deterministic during evaluation by setting a seed for the random number generator that defines the random behavior. The seed test checks that calling the `seed()` method with a constant actually makes the environment deterministic.

The seed test takes in a function that creates a pettingzoo environment. For example

```
from pettingzoo.test import seed_test
from pettingzoo.butterfly import pistonball_v3
env_fn = pistonball_v3.env
seed_test(env_fn, num_cycles=10)
```

The optional argument, `num_cycles`, indicates how long the environment will be run for to check determinism. Some environments only fail the test long after initialization.

### Max Cycles Test

The max cycles test tests that the `max_cycles` environment argument exists and the resulting environment actually runs for the correct number of cycles. If your environment does not take a `max_cycles` argument, you should not run this test. The reason this test exists is that there are a lot of one-off differences possible when implementing `max_cycles`. An example test usage looks like:

```
from pettingzoo.test import max_cycles_test
from pettingzoo.butterfly import pistonball_v3
env = pistonball_v3.env()
max_cycles_test(env)
```

### Render test

The render test checks that rendering 1) does not crash and 2) gives output of the correct type given a mode. The render test supports testing `'human'`, `'ansi'`, and `'rgb_array'` modes.

```
from pettingzoo.test import render_test
from pettingzoo.butterfly import pistonball_v3
env = pistonball_v3.env()
render_test(env)
```

### Performance benchmark test

To make sure we do not have performance regressions, we have the performance benchmark test. This test simply prints out the number of steps and cycles that the environment takes in 5 seconds. This test needs manual inspection to use:

```
from pettingzoo.test import performance_benchmark
from pettingzoo.butterfly import pistonball_v3
env = pistonball_v3.env()
performance_benchmark(env)
```

### Save observation test

The save observation test is to visually inspect the observations of games with graphical observations to make sure they are what is intended. We have found that observations are a huge source of bugs in environments, so it is good to manually check them when possible. This test just tries to save the observations of all the agents. If it fails, then it just prints a warning. The output needs to be visually inspected for correctness.

```
from pettingzoo.test import test_save_obs
from pettingzoo.butterfly import pistonball_v3
env = pistonball_v3.env()
test_save_obs(env)
```
