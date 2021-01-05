### Seed Test

To have a properly reproducible environment that utilizes randomness, you need to be able to make it deterministic during evaluation by setting a seed for the random number generator that defines the random behavior. The seed test checks that calling the `seed()` method with a constant actually makes the environment deterministic.

The seed test takes in a function that creates a pettingzoo environment. For example

```
from pettingzoo.test import seed_test
from pettingzoo.butterfly import pistonball_v3
env_fn = pistonball_v3.env
seed_test(env_fn)
```

## Utils

### Average Total Reward Util

The average total reward for an environment, as presented in the documentation, is summed over all agents over all steps in the episode, averaged over episodes.

This value is important for establishing the simplest possible baseline: the random policy. 

```
from pettingzoo.utils import average_total_reward
from pettingzoo.butterfly import pistonball_v3
env = pistonball_v3.env()
average_total_reward(env)
```
