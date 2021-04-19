# Developer Documentation

This documentation overviews creating new environments and relevant useful wrappers, utilities and tests included in PettingZoo designed for the creation of new environments.

## Example Custom Environment

This is a carefully commented version of the PettingZoo rock paper scissors environment.

```python
from gym.spaces import Discrete
import numpy as np
from pettingzoo import AECEnv
from pettingzoo.utils import agent_selector
from pettingzoo.utils import wrappers


ROCK = 0
PAPER = 1
SCISSORS = 2
NONE = 3
MOVES = ["ROCK", "PAPER", "SCISSORS", "None"]
NUM_ITERS = 100
REWARD_MAP = {
    (ROCK, ROCK): (0, 0),
    (ROCK, PAPER): (-1, 1),
    (ROCK, SCISSORS): (1, -1),
    (PAPER, ROCK): (1, -1),
    (PAPER, PAPER): (0, 0),
    (PAPER, SCISSORS): (-1, 1),
    (SCISSORS, ROCK): (-1, 1),
    (SCISSORS, PAPER): (1, -1),
    (SCISSORS, SCISSORS): (0, 0),
}


def env():
    '''
    The env function wraps the environment in 3 wrappers by default. These
    wrappers contain logic that is common to many pettingzoo environments.
    We recomend you use at least the OrderEnforcingWrapper on your own environment
    to provide sane error messages. You can find full documentation for these methods
    elsewhere in the developer documentation.
    '''
    env = raw_env()
    env = wrappers.CaptureStdoutWrapper(env)
    env = wrappers.AssertOutOfBoundsWrapper(env)
    env = wrappers.OrderEnforcingWrapper(env)
    return env


class raw_env(AECEnv):
    '''
    The metadata holds environment constants. From gym, we inherit the "render.modes",
    metadata which specifies which modes can be put into the render() method.
    At least human mode should be supported.
    The "name" metadata allows the environment to be pretty printed.
    '''
    metadata = {'render.modes': ['human'], "name": "rps_v1"}

    def __init__(self):
        '''
        The init method takes in environment arguments and
         should define the following attributes:
        - possible_agents
        - action_spaces
        - observation_spaces

        These attributes should not be changed after initialization.
        '''
        self.possible_agents = ["player_" + str(r) for r in range(2)]
        self.agent_name_mapping = dict(zip(self.possible_agents, list(range(len(self.possible_agents)))))

        # Gym spaces are defined and documented here: https://gym.openai.com/docs/#spaces
        self.action_spaces = {agent: Discrete(3) for agent in self.possible_agents}
        self.observation_spaces = {agent: Discrete(4) for agent in self.possible_agents}

    def render(self, mode="human"):
        '''
        Renders the environment. In human mode, it can print to terminal, open
        up a graphical window, or open up some other display that a human can see and understand.
        '''
        if len(self.agents) == 2:
            string = ("Current state: Agent1: {} , Agent2: {}".format(MOVES[self.state[self.agents[0]]], MOVES[self.state[self.agents[1]]]))
        else:
            string = "Game over"
        print(string)

    def observe(self, agent):
        '''
        Observe should return the observation of the specified agent. This function
        should return a sane observation (though not necessarily the most up to date possible)
        at any time after reset() is called.
        '''
        # observation of one agent is the previous state of the other
        return np.array(self.observations[agent])

    def close(self):
        '''
        Close should release any graphical displays, subprocesses, network connections
        or any other environment data which should not be kept around after the
        user is no longer using the environment.
        '''
        pass

    def reset(self):
        '''
        Reset needs to initialize the following attributes
        - agents
        - rewards
        - _cumulative_rewards
        - dones
        - infos
        - agent_selection
        And must set up the environment so that render(), step(), and observe()
        can be called without issues.

        Here it sets up the state dictionary which is used by step() and the observations dictionary which is used by step() and observe()
        '''
        self.agents = self.possible_agents[:]
        self.rewards = {agent: 0 for agent in self.agents}
        self._cumulative_rewards = {agent: 0 for agent in self.agents}
        self.dones = {agent: False for agent in self.agents}
        self.infos = {agent: {} for agent in self.agents}
        self.state = {agent: NONE for agent in self.agents}
        self.observations = {agent: NONE for agent in self.agents}
        self.num_moves = 0
        '''
        Our agent_selector utility allows easy cyclic stepping through the agents list.
        '''
        self._agent_selector = agent_selector(self.agents)
        self.agent_selection = self._agent_selector.next()

    def step(self, action):
        '''
        step(action) takes in an action for the current agent (specified by
        agent_selection) and needs to update
        - rewards
        - _cumulative_rewards (accumulating the rewards)
        - dones
        - infos
        - agent_selection (to the next agent)
        And any internal state used by observe() or render()
        '''
        if self.dones[self.agent_selection]:
            # handles stepping an agent which is already done
            # accepts a None action for the one agent, and moves the agent_selection to
            # the next done agent,  or if there are no more done agents, to the next live agent
            return self._was_done_step(action)

        agent = self.agent_selection

        # the agent which stepped last had its _cumulative_rewards accounted for
        # (because it was returned by last()), so the _cumulative_rewards for this
        # agent should start again at 0
        self._cumulative_rewards[agent] = 0

        # stores action of current agent
        self.state[self.agent_selection] = action

        # collect reward if it is the last agent to act
        if self._agent_selector.is_last():
            # rewards for all agents are placed in the .rewards dictionary
            self.rewards[self.agents[0]], self.rewards[self.agents[1]] = REWARD_MAP[(self.state[self.agents[0]], self.state[self.agents[1]])]

            self.num_moves += 1
            # The dones dictionary must be updated for all players.
            self.dones = {agent: self.num_moves >= NUM_ITERS for agent in self.agents}

            # observe the current state
            for i in self.agents:
                self.observations[i] = self.state[self.agents[1 - self.agent_name_mapping[i]]]
        else:
            # necessary so that observe() returns a reasonable observation at all times.
            self.state[self.agents[1 - self.agent_name_mapping[agent]]] = NONE
            # no rewards are allocated until both players give an action
            self._clear_rewards()

        # selects the next agent.
        self.agent_selection = self._agent_selector.next()
        # Adds .rewards to ._cumulative_rewards
        self._accumulate_rewards()

```

## Example Custom Parallel Environment

```python
from gym.spaces import Discrete
from pettingzoo import ParallelEnv
from pettingzoo.utils import wrappers
from pettingzoo.utils import from_parallel


ROCK = 0
PAPER = 1
SCISSORS = 2
NONE = 3
MOVES = ["ROCK", "PAPER", "SCISSORS", "None"]
NUM_ITERS = 100
REWARD_MAP = {
    (ROCK, ROCK): (0, 0),
    (ROCK, PAPER): (-1, 1),
    (ROCK, SCISSORS): (1, -1),
    (PAPER, ROCK): (1, -1),
    (PAPER, PAPER): (0, 0),
    (PAPER, SCISSORS): (-1, 1),
    (SCISSORS, ROCK): (-1, 1),
    (SCISSORS, PAPER): (1, -1),
    (SCISSORS, SCISSORS): (0, 0),
}


def env():
    '''
    The env function wraps the environment in 3 wrappers by default. These
    wrappers contain logic that is common to many pettingzoo environments.
    We recomend you use at least the OrderEnforcingWrapper on your own environment
    to provide sane error messages. You can find full documentation for these methods
    elsewhere in the developer documentation.
    '''
    env = raw_env()
    env = wrappers.CaptureStdoutWrapper(env)
    env = wrappers.AssertOutOfBoundsWrapper(env)
    env = wrappers.OrderEnforcingWrapper(env)
    return env


def raw_env():
    '''
    To support the AEC API, the raw_env() function just uses the from_parallel
    function to convert from a ParallelEnv to an AEC env
    '''
    env = parallel_env()
    env = from_parallel(env)
    return env


class parallel_env(ParallelEnv):
    metadata = {'render.modes': ['human'], "name": "rps_v1"}

    def __init__(self):
        '''
        The init method takes in environment arguments and should define the following attributes:
        - possible_agents
        - action_spaces
        - observation_spaces

        These attributes should not be changed after initialization.
        '''
        self.possible_agents = ["player_" + str(r) for r in range(2)]
        self.agent_name_mapping = dict(zip(self.possible_agents, list(range(len(self.possible_agents)))))

        # Gym spaces are defined and documented here: https://gym.openai.com/docs/#spaces
        self.action_spaces = {agent: Discrete(3) for agent in self.possible_agents}
        self.observation_spaces = {agent: Discrete(4) for agent in self.possible_agents}

    def render(self, mode="human"):
        '''
        Renders the environment. In human mode, it can print to terminal, open
        up a graphical window, or open up some other display that a human can see and understand.
        '''
        if len(self.agents) == 2:
            string = ("Current state: Agent1: {} , Agent2: {}".format(MOVES[self.state[self.agents[0]]], MOVES[self.state[self.agents[1]]]))
        else:
            string = "Game over"
        print(string)

    def close(self):
        '''
        Close should release any graphical displays, subprocesses, network connections
        or any other environment data which should not be kept around after the
        user is no longer using the environment.
        '''
        pass

    def reset(self):
        '''
        Reset needs to initialize the `agents` attribute and must set up the
        environment so that render(), and step() can be called without issues.

        Here it initializes the `num_moves` variable which counts the number of
        hands that are played.

        Returns the observations for each agent
        '''
        self.agents = self.possible_agents[:]
        self.num_moves = 0
        observations = {agent: NONE for agent in self.agents}
        return observations

    def step(self, actions):
        '''
        step(action) takes in an action for each agent and should return the
        - observations
        - rewards
        - dones
        - infos
        dicts where each dict looks like {agent_1: item_1, agent_2: item_2}
        '''
        # If a user passes in actions with no agents, then just return empty observations, etc.
        if not actions:
            self.agents = []
            return {}, {}, {}, {}

        # rewards for all agents are placed in the rewards dictionary to be returned
        rewards = {}
        rewards[self.agents[0]], rewards[self.agents[1]] = REWARD_MAP[(actions[self.agents[0]], actions[self.agents[1]])]

        self.num_moves += 1
        env_done = self.num_moves >= NUM_ITERS
        dones = {agent: env_done for agent in self.agents}

        # current observation is just the other player's most recent action
        observations = {self.agents[i]: int(actions[self.agents[1 - i]]) for i in range(len(self.agents))}

        # typically there won't be any information in the infos, but there must
        # still be an entry for each agent
        infos = {agent: {} for agent in self.agents}

        return observations, rewards, dones, infos

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

```
from pettingzoo.utils import to_parallel
from pettingzoo.butterfly import pistonball_v4
env = pistonball_v4.env()
env = to_parallel(env)
```

#### Parallel to AEC

Any parallel environment can be efficiently converted to an AEC environment with the `from_parallel` wrapper.

```
from pettingzoo.utils import from_parallel
from pettingzoo.butterfly import pistonball_v4
env = pistonball_v4.parallel_env()
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

```
from pettingzoo.utils import OrderEnforcingWrapper
from pettingzoo.butterfly import pistonball_v4
env = pistonball_v4.env()
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
```
from pettingzoo.utils.deprecated_module import DeprecatedModule
prospector_v0 = DeprecatedModule("prospector", "v0", "v3")
```
This declaration tells the user that `prospector_v0` is deprecated and `prospector_v4` should be used instead. In particular, it gives the following error:
```
from pettingzoo.butterfly import prospector_v0
prospector_v0.env()
# pettingzoo.utils.deprecated_module.DeprecatedEnv: prospector_v0 is now deprecated, use prospector_v4 instead
```

## Tests

PettingZoo has a number of compliance tests for environments through. If you are adding a new environment, we encourage you to run these tests on your own environment.

### API Test

PettingZoo's API has a number of features and requirements. To make sure your environment is consistent with the API, we have the api_test. Below is an example:

```
from pettingzoo.test import api_test
from pettingzoo.butterfly import pistonball_v4
env = pistonball_v4.env()
api_test(env, num_cycles=10, verbose_progress=False)
```

As you can tell, you simply pass an environment to the test. The test will assert or give some other error on an API issue, and will return normally if it passes.

The optional arguments are:

*  `num_cycles`: runs the environment for that many cycles and checks that the output is consistent with the API.
* `verbose_progress`: Prints out messages to indicate partial completion of the test. Useful for debugging environments.

### Parallel API Test

This is an analogous version of the API test, but for parallel environments. You can use this test like:

```
from pettingzoo.test import parallel_api_test
from pettingzoo.butterfly import pistonball_v4
env = pistonball_v4.parallel_env()
parallel_api_test(env, num_cycles=10)
```

### Seed Test

To have a properly reproducible environment that utilizes randomness, you need to be able to make it deterministic during evaluation by setting a seed for the random number generator that defines the random behavior. The seed test checks that calling the `seed()` method with a constant actually makes the environment deterministic.

The seed test takes in a function that creates a pettingzoo environment. For example

```
from pettingzoo.test import seed_test
from pettingzoo.butterfly import pistonball_v4
env_fn = pistonball_v4.env
seed_test(env_fn, num_cycles=10, test_kept_state=True)
```

Internally, there are two separate tests.

1. Do two separate environments give the same result after the environment is seeded?
2. Does a single environment give the same result after seed() then reset() is called?

The first optional argument, `num_cycles`, indicates how long the environment will be run to check for determinism. Some environments only fail the test long after initialization.

The second optional argument, `test_kept_state` allows the user to disable the second test. Some physics based environments fail this test due to barely detectable differences due to caches, etc, which are not important enough to matter.

### Max Cycles Test

The max cycles test tests that the `max_cycles` environment argument exists and the resulting environment actually runs for the correct number of cycles. If your environment does not take a `max_cycles` argument, you should not run this test. The reason this test exists is that many off-by-one errors are possible when implementing `max_cycles`. An example test usage looks like:

```
from pettingzoo.test import max_cycles_test
from pettingzoo.butterfly import pistonball_v4
env = pistonball_v4.env()
max_cycles_test(env)
```

### Render Test

The render test checks that rendering 1) does not crash and 2) produces output of the correct type when given a mode (only supports `'human'`, `'ansi'`, and `'rgb_array'` modes).

```
from pettingzoo.test import render_test
from pettingzoo.butterfly import pistonball_v4
env = pistonball_v4.env()
render_test(env)
```

The render test method takes in an optional argument `custom_tests` that allows for additional tests in non-standard modes.

```
custom_tests = {
    "svg": lambda render_result: return isinstance(render_result, str)
}
render_test(env, custom_tests=custom_tests)
```

### Performance Benchmark Test

To make sure we do not have performance regressions, we have the performance benchmark test. This test simply prints out the number of steps and cycles that the environment takes in 5 seconds. This test requires manual inspection of its outputs:

```
from pettingzoo.test import performance_benchmark
from pettingzoo.butterfly import pistonball_v4
env = pistonball_v4.env()
performance_benchmark(env)
```

### Save Observation Test

The save observation test is to visually inspect the observations of games with graphical observations to make sure they are what is intended. We have found that observations are a huge source of bugs in environments, so it is good to manually check them when possible. This test just tries to save the observations of all the agents. If it fails, then it just prints a warning. The output needs to be visually inspected for correctness.

```
from pettingzoo.test import test_save_obs
from pettingzoo.butterfly import pistonball_v4
env = pistonball_v4.env()
test_save_obs(env)
```
