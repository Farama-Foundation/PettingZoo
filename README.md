# PettingZoo
PettingZoo is Python library for conducting research in multi-agent reinforcement learning. It's akin to a multi-agent version of OpenAI's Gym library.


## Environment Types and Installation

PettingZoo includes the following sets of games:

* atari: Multi-player Atari 2600 games (both cooperative and competitive)
* classic: Classical, nongraphical, competitive games (i.e. chess, Texas hold 'em, and go)
* gamma: Cooperative graphical games developed by us. Policies for these must learn very coordinated behaviors.
* magent: Environments with massive numbers of particle agents, originally from https://github.com/geek-ai/MAgent
* mpe: A set of simple nongraphical communication tasks, originally from https://github.com/openai/multiagent-particle-envs
* sisl: 3 cooperative environments, originally from https://github.com/sisl/MADRL

To install a set of games, use `pip3 install pettingzoo[atari]` (or whichever set of games you want).

We support Python 3.6, 3.7 and 3.8.


## Initializing Environments

Using environments in PettingZoo is very similar to Gym, i.e. you initialize an environment via:

```
from pettingzoo.gamma import pistonball
env = pistonball.env()
```

Environments are generally highly configurable via arguments at creation, i.e.:

```
cooperative_pong.env(ball_velocity=?, left_paddle_velocity=?,
right_paddle_velocity=?, wedding_cake_paddle=True, max_frames=900)
```

## Interacting With Environments
Environments can be interacted with in a manner very similar to Gym:

```
observation = env.reset()
while True:
    for _ in env.agent_order:
        reward, done, info = env.last()
        action = policy(observation)
        observation = env.step(action)
```

The commonly used methods are:

`agent_order` is a list of agent names in the order they act. In some environments, the number of agents and this order can change. Agent's can also appear twice in this (i.e. act twice in a cycle).

`last()` returns the reward, etc. from the action taken by the selected agent during it's last step. This is because those values aren't guaranteed to be fully known until right before an agent's next turn.

`agent_selection` is used to let all the functions know what agent is acting (and is why agent isn't passed as an argument above).

`reset(observe=True)` is the same as in Gym- it resets the environment (and set's it up for use when called the first time), and returns the observation of the first agent in `agent order`. Setting `observe=False` disables computing and returning the observation.

`step(action, observe=True)` takes the action of the agent in the environment, automatically switches control to the next agent in `env.agent_order`, and returns the observation for the next agent (as it's what the policy will next need). Setting `observe=False` disables computing and returning the observation.


## Advanced Environment API
When working in multi-agent learning, there are many fantastically weird cases. Because of this, our API includes lower level functions and attributes that you probably won't need, but are very important when you do. Their functionality is also needed to implement by the high level functions above, so implementing them is just a matter of code factoring.

`agents`: A list of the names of all current agents, typically integers. These may be changed as an environment progresses (i.e. agents can be added or removed).

`observation_spaces`: A dict of the gym observation spaces of every agent, by name.

`action_spaces`: A dict of the gym action spaces of every agent, by name.

`rewards`: A dict of the rewards of every agent at the time called, by name. Rewards are summed from the last time an agent took it's turn, and zeroed before it takes another turn. This is called by `last`. This looks like:

`{0:[first agent's reward], 1:[second agent's reward] ... n-1:[nth agent's reward]}`

`dones`: A dict of the done state of every agent at the time called, by name. This is called by `last`. This looks like:

`dones = {0:[first agent's done state], 1:[second agent's done state] ... n-1:[nth agent's done state]}`

`infos`: A dict of info for each agent, by name. Each agent's info is also a dict. This is called by `last`. This looks like:

`infos = {0:[first agent's info], 1:[second agent's info] ... n-1:[nth agent's info]}`.

`observe(agent)`: Returns the observation an agent currently can make. `step` calls this.

`render(mode='human')`: Displays a rendered frame from the environment, if supported. Environments may support different render modes.

`close()`: Closes the rendering window.


## Environment Documentation

Full documentation of each environment is available [here].

## Other Utils

### API Test

```
import pettingzoo.tests.api_test as api_test
api_test.api_test(env, render=True, manual_control=True, save_obs=True)
```

This tests the environment for API compliance. `render=True` tests render functionality, if an environment has it. `manual_control` tests for manual_control functionality if included (explained below). Set `save_obs=True` to save observations from the directory to the command is run in as .png files. This is very helpful for debugging graphical environments.

### Bombardment Test

```
import pettingzoo.tests.bombardment_test as bombardment_test
bombardment_test.bombardment_test(env, cycles=10000)
```

This randomly plays through the environment `cycles` times, to test for stability.

### Performance Test

```
import pettingzoo.tests.performance_benchmark as performance_benchmark
performance_benchmark.performance_benchmark(env)
```

This randomly steps through the environment for 60 seconds to benchmark it's performance.

### Manual Control

Often, you want to be able to play before trying to learn it to get a better feel for it. Some of our games directly support this:

```
from pettingzoo.gamma import prison
pistonball.manual_control([environment specs])
```

Look at [the documentation] for individual environments to see which supports manual control and what the controls for a specific environment are.

### Random Demo

For all renderable games games, including those that can't be played by humans, you easily can get an impression for them by watching a random policy control all the actions:

```
from pettingzoo.utils import random_demo
random_demo(env)
```


## OS Support

We support Linux and macOS, and conduct CI testing on both. We will accept PRs related to windows, but do not officially support it. We're open to help properly supporting Windows.


## Leaderboards
Our cooperative games have leaderboards for best total (summed over all agents) score. If you'd like to be listed on the leader board, please submit a pull request. Only pull requests that link to code for reproducibility and use environment arguments in the spirit of the competition will be accepted.


# Development Notes

## Creating Custom Environments
Creating a custom environment with PettingZoo should roughly look like the following:

```
from pettingzoo import AECEnv
from pettingzoo.utils import agent_selector
from gym import spaces


class env(AECEnv):
    metadata = {'render.modes': ['human']} # only add if environment supports rendering

    def __init__(self, arg1, arg2, ...):
        super(env, self).__init__()

        self.agents = [0, 1 ... n] # agent names
        self.agent_order = # list of agent names in the order they act in a cycle. Usually this will be the same as the agents list.
        self.observation_spaces = # dict of observation spaces for each agent, from gym.spaces
        self.action_spaces = # dict of action spaces for each agent, from gym.spaces
        self.rewards = {0:[first agent's reward], 1:[second agent's reward] ... n-1:[nth agent's reward]}
        self.dones = {0:[first agent's done state], 1:[second agent's done state] ... n-1:[nth agent's done state]}
        self.infos = {0:[first agent's info], 1:[second agent's info] ... n-1:[nth agent's info]}

        # agent selection stuff
        self._agent_selector = agent_selector(self.agent_order)

        # Initialize game stuff

    def observe(self, agent):
        # return observation of an agent
        return observation

    def step(self, action, observe=True):
        # Do game stuff on the selected agent

        # Switch selection to next agents
        self.agent_selection = self._agent_selector.next()

        if observe:
            return self.observe(self.agent_selection)
        else:
            return

    # last is added as a part of the AECEnv class, don't write it yourself

    def reset(self, observe=True):
        # reset environment

        # selects the first agent
        self._agent_selector.reinit(self.agent_order)
        self.agent_selection = self._agent_selector.next()
        if observe:
            return self.observe(self.agent_selection)
        else:
            return

    def render(self, mode='human'): # not all environments will support rendering
        ...

    def close(self):
        ...
```

## Incomplete Environments

The following environments are under active development:

* atari/* (Ben)
* classic/checkers (Tianchen)
* classic/connect_four (Praveen)
* classic/go (Luis)
* classic/hanabi (Clemens)
* gamma/prospector (Yashas)
* magent/* (David and Mario)

Development has not yet started on:

* classic/backgammon
* classic/shogi (python-shogi)
