# Testing Environments

PettingZoo has a number of compliance tests for environments through. If you are adding a new environment, we encourage you to run these tests on your own environment.

## API Test

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

## Parallel API Test

This is an analogous version of the API test, but for parallel environments. You can use this test like:

``` python
from pettingzoo.test import parallel_api_test
from pettingzoo.butterfly import pistonball_v6
env = pistonball_v6.parallel_env()
parallel_api_test(env, num_cycles=1000)
```

## Seed Test

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

## Render Test

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

## Performance Benchmark Test

To make sure we do not have performance regressions, we have the performance benchmark test. This test simply prints out the number of steps and cycles that the environment takes in 5 seconds. This test requires manual inspection of its outputs:

``` python
from pettingzoo.test import performance_benchmark
from pettingzoo.butterfly import pistonball_v6
env = pistonball_v6.env()
performance_benchmark(env)
```

## Save Observation Test

The save observation test is to visually inspect the observations of games with graphical observations to make sure they are what is intended. We have found that observations are a huge source of bugs in environments, so it is good to manually check them when possible. This test just tries to save the observations of all the agents. If it fails, then it just prints a warning. The output needs to be visually inspected for correctness.

``` python
from pettingzoo.test import test_save_obs
from pettingzoo.butterfly import pistonball_v6
env = pistonball_v6.env()
test_save_obs(env)
```
