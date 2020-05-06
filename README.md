# PettingZoo
PettingZoo is Python library for conducting research in multi-agent reinforcement learning. It's akin to a multi-agent version of OpenAI's Gym library.

We model environments as *Agent Environment Cycle* (AEC) games, in order to be able to support all types of multi-agent RL environments under one API.

## Environment Types and Installation

PettingZoo includes the following sets of games:

* atari: Multi-player Atari 2600 games (both cooperative and competitive)
* classic: Classical, nongraphical, competitive games (i.e. chess, Texas hold 'em, and go)
* gamma: Cooperative graphical games developed by us. Policies for these must learn very coordinated behaviors.
* magent: Environments with massive numbers of particle agents, originally from https://github.com/geek-ai/MAgent
* mpe: A set of simple nongraphical communication tasks, originally from https://github.com/openai/multiagent-particle-envs
* sisl: 3 cooperative environments, originally from https://github.com/sisl/MADRL

To install, use `pip install pettingzoo` 

We support Python 3.6, 3.7 and 3.8


## Initializing Environments

Using environments in PettingZoo is very similar to Gym, i.e. you initialize an environment via:

```
from pettingzoo.gamma import pistonball_v0
env = pistonball_v0.env()
```

Environments are generally highly configurable via arguments at creation, i.e.:

```
cooperative_pong.env(ball_speed=18, left_paddle_speed=25,
right_paddle_speed=25, is_cake_paddle=True, max_frames=900, bounce_randomness=False)
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


## Additional Environment API

PettingZoo models games as AEC games, and thus can support any game multi-agent RL can consider, allowing for fantastically weird cases. Because of this, our API includes lower level functions and attributes that you probably won't need, but are very important when you do. Their functionality is also needed by the high level functions above though, so implementing them is just a matter of code factoring.

`agents`: A list of the names of all current agents, typically integers. These may be changed as an environment progresses (i.e. agents can be added or removed).

`num_agents`: The number of agents currently in the environment.

`observation_spaces`: A dict of the gym observation spaces of every agent, by name.

`action_spaces`: A dict of the gym action spaces of every agent, by name.

`rewards`: A dict of the rewards of every agent at the time called, by name. Rewards are summed from the last time an agent took it's turn, and zeroed before it takes another turn. This is called by `last`. This looks like:

`{0:[first agent's reward], 1:[second agent's reward] ... n-1:[nth agent's reward]}`

`dones`: A dict of the done state of every agent at the time called, by name. This is called by `last`. This looks like:

`dones = {0:[first agent's done state], 1:[second agent's done state] ... n-1:[nth agent's done state]}`

`infos`: A dict of info for each agent, by name. Each agent's info is also a dict. This is called by `last`. This looks like:

`infos = {0:[first agent's info], 1:[second agent's info] ... n-1:[nth agent's info]}`

`observe(agent)`: Returns the observation an agent currently can make. `step` calls this.

`render(mode='human')`: Displays a rendered frame from the environment, if supported. Environments may support different render modes.

`close()`: Closes the rendering window.

## Environment Actions

In this API, when the environment acts following an agents action, they're treated as happening at the same time. There are cases where breaking these apart can be very helpful. Our API supports this by treating the environment as an "agent". While initially odd, having an environment agent that can act on the state of the game is actually a common modeling practice in game theory.

We encourage calling the environment actor `'env'` in `env.agents`, and having it take `None` as an action.

## Environment Documentation

Full documentation of each environment is available [here].

All environments end in something like \_v0.  When changes are made to environments that might impact learning results, the number is increased by one to prevent potential confusion.

## SuperSuit

[SuperSuit](https://github.com/PettingZoo-Team/SuperSuit) contains nice wrappers to do common preprocessing actions, like frame stacking or changing RGB observations to greyscale. It also supports Gym environments, in addition to PettingZoo.

## Utils

### API Test

```
import pettingzoo.tests.api_test as api_test
api_test.api_test(env, render=True, manual_control=None, save_obs=False)
```

This tests the environment for API compliance. `render=True` tests render functionality, if an environment has it. `manual_control` tests for manual_control functionality if included (explained below). Set `save_obs=True` to save observations as .png images in the directory the command is run in for debugging purposes (this only supports enviornment with image observations). `manual_control` takes the manual control method name for an environment (i.e. `manual_control=pistonball.manual_control`) to run the test.

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
prison.manual_control([environment specs])
```

Look at the [documentation] for individual environments to see which supports manual control and what the controls for a specific environment are.

### Random Demo

For all renderable games games, including those that can't be played by humans, you easily can get an impression for them by watching a random policy control all the actions:

```
from pettingzoo.utils import random_demo
random_demo(env)
```

### Observation Saver

If the agents in a game make observations that are images, the observations can be saved to an image file. This function takes in the environment, along with a specified agent. If no agent is specified, the current selected agent for the environment is chosen. If all_agents is passed in as True, then the observations of all agents in the environment is saved. By default the images are saved to the current working directory, in a folder matching the environment name. The saved image will match the name of the observing agent. If save_dir is passed in, a new folder is created where images will be saved to.

```
from pettingzoo.utils import save_observation
save_observation(env, agent=None, all_agents=False, save_dir=os.getcwd())

```

The first function will save the current observation for the specified agent. The second function will save the current observation based on the currently selected agent. The last function will save the current observations of all agents in the environment.

## OS Support

We support Linux and macOS, and conduct CI testing on both. We will accept PRs related to windows, but do not officially support it. We're open to help properly supporting Windows.


## Leaderboards
Our cooperative games have leaderboards for best total (summed over all agents) score. If you'd like to be listed on the leader board, please submit a pull request. Only pull requests that link to code for reproducibility and use environment arguments in the spirit of the competition will be accepted.

## Incomplete Environments

The following environments are under active development:

* atari/* (Ben)
* classic/checkers (Ben)
* classic/go (Luis)
* classic/hanabi (Clemens)
* gamma/prospector (Yashas)
* magent/* (Mario)
* robotics/* (Yiling)
* classic/backgammon (Caroline)

Development has not yet started on:

* classic/shogi (python-shogi)
