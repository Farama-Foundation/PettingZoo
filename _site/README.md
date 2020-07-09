# PettingZoo
[![Build Status](https://travis-ci.com/PettingZoo-Team/PettingZoo.svg?branch=master)](https://travis-ci.com/PettingZoo-Team/PettingZoo)

PettingZoo is a Python library for conducting research in multi-agent reinforcement learning. It's akin to a multi-agent version of OpenAI's Gym library.

We model environments as *Agent Environment Cycle* (AEC) games, in order to be able to support all types of multi-agent RL environments under one API.

## Environment Types and Installation

PettingZoo includes the following sets of games:

* atari: Multi-player Atari 2600 games (both cooperative and competitive)
* classic: Classical games including card games, board games, etc.
* butterfly: Cooperative graphical games developed by us, requiring a high degree of coordination
* magent: Configurable environments with massive numbers of particle agents, originally from https://github.com/geek-ai/MAgent
* mpe: A set of simple nongraphical communication tasks, originally from https://github.com/openai/multiagent-particle-envs
* sisl: 3 cooperative environments, originally from https://github.com/sisl/MADRL

To install, use `pip install pettingzoo`

We support Python 3.6, 3.7 and 3.8


## Initializing Environments

Using environments in PettingZoo is very similar to Gym, i.e. you initialize an environment via:

```
from pettingzoo.butterfly import pistonball_v0
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
for agent in env.agent_iter():
    reward, done, info = env.last()
    action = policy(observation)
    observation = env.step(action)
```

The commonly used methods are:

`agent_iter(max_agent_iter=2**63)` returns an iterator that yields the current agent of the environment. It terminates when all agents in the environment are done or when `max_agent_iter` (steps have been executed).

`last()` returns the total reward the agent has received since it's last step and present, if the agent is done, anything in info associated with the selected agent.

`reset(observe=True)` resets the environment (and sets it up for use when called the first time), and returns the observation of the first agent in `agent order`. Setting `observe=False` disables computing and returning the observation.

`step(action, observe=True)` takes the action of the agent in the environment, automatically switches control to the next agent, and *returns the observation for the next agent* (as it's what the policy will next need). Setting `observe=False` disables computing and returning the observation.


## Additional Environment API

PettingZoo models games as AEC games, and thus can support any game multi-agent RL can consider, allowing for fantastically weird cases. Because of this, our API includes lower level functions and attributes that you probably won't need, but are very important when you do. Their functionality is also needed by the high level functions above though, so implementing them is just a matter of code factoring.

`agents`: A list of the names of all current agents, typically integers. These may be changed as an environment progresses (i.e. agents can be added or removed).

`agent_selection` an attribute of the environment corresponding to the currently selected agent that an action can be taken for. Internal functions use it to know what agent is acting.

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
api_test.api_test(env, render=False, verbose_progress=False)
```

This tests the environment for API compliance. If the environment has a custom `render()` method, setting argument `render=True` tests whether there is an accompanying custom `close()` method. If `verbose_progress=True`, progress of the test is printed to the console.

### Bombardment Test

```
import pettingzoo.tests.bombardment_test as bombardment_test
bombardment_test.bombardment_test(env, cycles=10000)
```

This randomly plays through the environment `cycles` times, to test for stability.

### Performance Benchmark

```
import pettingzoo.tests.performance_benchmark as performance_benchmark
performance_benchmark.performance_benchmark(env)
```

This randomly steps through the environment for 60 seconds to benchmark it's performance.

### Manual Control Test

```
import pettingzoo.tests.manual_control_test as manual_control_test
manual_control_test.test_manual_control(env.manual_control)
```

If the environment has`manual_control` functionality included (explained below), this test makes sure the method does not creash for random key inputs. The argument supplied to the `test_manual_control` method is the manual control method name for the environment (i.e. `manual_control=pistonball.manual_control`).

### Manual Control

Often, you want to be able to play before trying to learn it to get a better feel for it. Some of our games directly support this:

```
from pettingzoo.butterfly import prison
prison.manual_control([environment specs])
```

Look at the [documentation] for individual environments to see which supports manual control and what the controls for a specific environment are.

### Random Demo

For all renderable games, including those that can't be played by humans, you easily can get an impression for them by watching a random policy control all the actions:

```
from pettingzoo.utils import random_demo
random_demo(env)
```

### Observation Saving

If the agents in a game make observations that are images, the observations can be saved to an image file. This function takes in the environment, along with a specified agent. If no agent is specified, the current selected agent for the environment is chosen. If all_agents is passed in as True, then the observations of all agents in the environment is saved. By default the images are saved to the current working directory, in a folder matching the environment name. The saved image will match the name of the observing agent. If save_dir is passed in, a new folder is created where images will be saved to.

```
from pettingzoo.utils import save_observation
save_observation(env, agent=None, all_agents=False, save_dir=os.getcwd())

```

The first function will save the current observation for the specified agent. The second function will save the current observation based on the currently selected agent. The last function will save the current observations of all agents in the environment.

## OS Support

We support Linux and macOS, and conduct CI testing on both. We will accept PRs related to Windows, but do not officially support it. We're open to help properly supporting Windows.

## Leaderboards
Our cooperative games have leaderboards for best total (summed over all agents) score. If you'd like to be listed on the leader board, please submit a pull request. Only pull requests that link to code for reproducibility and use environment arguments in the spirit of the competition will be accepted.

## Citation

To cite this project in publication, please use

```
@misc{pettingZoo2020,
  author = {Terry, Justin K and Black, Benjamin and Jayakumar, Mario  and Hari, Ananth and Santos, Luis and Dieffendahl, Clemens and Williams, Niall and Ravi, Praveen and Lokesh, Yashas and Horsch, Caroline and Patel, Dipam},
  title = {Petting{Z}oo},
  year = {2020},
  publisher = {GitHub},
  note = {GitHub repository},
  howpublished = {\url{https://github.com/PettingZoo-Team/PettingZoo}}
}
```

## Reward Program

We have a sort bug/documentation error bounty program, inspired by [Donald Knuth's reward checks](https://en.wikipedia.org/wiki/Knuth_reward_check). People who make mergable PRs which properly address meaningful problems in the code, or which make meaningful improvements to the documentation, can recieve a negotiable check for "hexadecimal dollar" ($2.56) mailed to them, or sent to them via PayPal. To redeem this, just send an email to justinkterry@gmail.com with your mailing adress or PayPal adress. We also pay out 32 cents for small fixes. This reward extends to libraries maintained by the PettingZoo team that PettingZoo depends on.
