
# Example custom environment

This is a carefully commented version of the PettingZoo rps environment. 

```python
from gym.spaces import Discrete
import numpy as np
from pettingzoo import AECEnv
from pettingzoo.utils import agent_selector
from pettingzoo.utils import wrappers

# Game specific global constants can just be put in the file
ROCK = 0
PAPER = 1
SCISSORS = 2
NONE = 3
MOVES = ["ROCK", "PAPER", "SCISSORS", "None"]
NUM_ITERS = 100


def env():
    '''
    The env function wraps the environment in 3 wrappers by default. These
    wrappers contain logic that is common to many pettingzoo environments.
    We recomend you use at least the OrderEnforcingWrapper on your own environment
    to provide sane error message. You can
    find full documentation for these methods elsewhere in the developer documentation.
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
    The "name"  metadata allows the environment to be pretty printed.
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

        self.action_spaces = {agent: Discrete(3) for agent in self.possible_agents}
        self.observation_spaces = {agent: Discrete(4) for agent in self.possible_agents}

        self.display_wait = 0.0

    def render(self, mode="human"):
        '''
        Renders the environment. In human mode, it can print to terminal, open
        up a graphical window, or open up some other way a human can see and understand.
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
        or any other environment data which should  not be kept around after the
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

        Here it sets up the state dictionary
        which is used by step() and the observations dictionary which is used by step()
        and observe()
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
            # handles stepping an agent which is done
            # takes in the None action, and moved agent_selection to the next
            # done agent or if there are no more done agents, to the next live agent
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
            self.rewards[self.agents[0]], self.rewards[self.agents[1]] = {
                (ROCK, ROCK): (0, 0),
                (ROCK, PAPER): (-1, 1),
                (ROCK, SCISSORS): (1, -1),
                (PAPER, ROCK): (1, -1),
                (PAPER, PAPER): (0, 0),
                (PAPER, SCISSORS): (-1, 1),
                (SCISSORS, ROCK): (-1, 1),
                (SCISSORS, PAPER): (1, -1),
                (SCISSORS, SCISSORS): (0, 0),
            }[(self.state[self.agents[0]], self.state[self.agents[1]])]

            self.num_moves += 1
            # The dones dictionary must be updated for all players.
            self.dones = {agent: self.num_moves >= NUM_ITERS for agent in self.agents}

            # observe the current state
            for i in self.agents:
                self.observations[i] = self.state[self.agents[1 - self.agent_name_mapping[i]]]
        else:
            # necessary so that observe() returns a reasonable observation at all times.
            self.state[self.agents[1 - self.agent_name_mapping[agent]]] = NONE
            # no rewards are allocated until both players give ann action
            self._clear_rewards()

        # selects the next agent.
        self.agent_selection = self._agent_selector.next()
        # Adds .rewards to ._cumulative_rewards
        self._accumulate_rewards()

```

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
