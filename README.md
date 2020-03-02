# PettingZoo
PettingZoo is Python library for conducting research in multi-agent reinforcement learning. It's akin to a multi-agent version of OpenAI's Gym library.


## Environment Types and Installation

PettingZoo includes the following sets of games:

* atari: Multi-player Atari 2600 games (both cooperative and competative)
* classic: Classical, nongraphical, competative games (i.e. chess, Texas hold 'em, and go)
* gamma: Cooperative graphical games developed by us. Policies for these must learn very coordinated behaviors.
* magent: Environments with massive numbers of particle agents, originally from https://github.com/geek-ai/MAgent
* mpe: A set of simple nongraphical communication tasks, originally from https://github.com/openai/multiagent-particle-envs
* robotics: A collection of 3D multi-agent robot environments, simulated with MuJoCo
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
        reward, done, info = env.last_cycle() 
        action = policy(observation)
        observation = env.step(action)
```

The commonly used methods are:

`agent_order` is a list of agent names in the order they act. In some environments, the number of agents and this order can change. Agent's can also appear twice in this (i.e. act twice in a cycle).

`last_cycle()` returns the reward, etc. from the action taken by the selected agent during it's last step. This is because those values aren't guaranteed to be fully known until right before an agent's next turn.

`agent_selection` is used to let all the functions know what agent is acting (and is why agent isn't passed as an argument above).

`reset(observe=True)` is the same as in Gym- it resets the environment (and set's it up for use when called the first time), and returns the observation of the first agent in `agent order`. Setting `observe=False` disables computing and returning the observation.

`step(action, observe=True)` takes the action of the agent in the environment, automatically switches control to the next agent in `env.agent_order`, and returns the observation for the next agent (as it's what the policy will next need). Setting `observe=False` disables computing and returning the observation.

## Advanced Environment API
When working in multi-agent learning, there are many fantastically weird cases. Because of this, our API includes lower level functions and attributes that you probably won't need, but are very important when you do. Their functionality is also needed to implement by the high level functions above, so implementing them is just a matter of code factoring.

`agents`: A list of the names of all current agents, typically integers. These may be changed as an environment progresses (i.e. agents can be added or removed).

`observation_spaces`: A dict of the gym observation spaces of every agent, by name.

`action_spaces`: A dict of the gym action spaces of every agent, by name.

`rewards`: A dict of the rewards of every agent at the time called, by name. Rewards are summed from the last time an agent took it's turn, and zeroed before it takes another turn. This is called by `last_cycle`. This looks like:

`{0:[first agent's reward], 1:[second agent's reward] ... n-1:[nth agent's reward]}`

`dones`: A dict of the done state of every agent at the time called, by name. This is called by `last_cycle`. This looks like: 

`dones = {0:[first agent's done state], 1:[second agent's done state] ... n-1:[nth agent's done state]}`

`infos`: A dict of info for each agent, by name. This is called by `last_cycle`. This looks like:

`infos = {0:[first agent's info], 1:[second agent's info] ... n-1:[nth agent's info]}`

`observe(agent)`: Returns the observation an agent currently can make. `step` calls this.

`render(mode='human')`: Displays a rendered frame from the environment, if supported. Environments may support different render modes, such as `rgb_array` (which returns numpy arrays of the screen).

`close()`: Closes the rendering window.

## Observation Wrapper

We include popular preprocessing methods out of the box:

```
from pettingzoo.utils import wrapper
env = wrapper(env, color_reduction=None, down_scale=(x_scale, y_scale), reshape=None,
range_scale=(obs_min, obs_max), new_dtype=None, frame_stacking=1)
```

*Frame stacking* stacks the 4 most recent frames on "top of" each other. For vector games observed via plain vectors (1D arrays), the output is just concatenated to a longer 1D array. For games via observed via graphical outputs (a 2D or 3D array), the arrays are stacked to be taller 3D arrays. Frame stacking is used to let policies get a sense of time from the environments. The argument to frame stacking controls how many frames back are stacked. At the start of the game, frames that don't yet exist are filled with 0s. An argument of 1 is analogous to being turned off.

*Color reduction* removes color information from game outputs to easier processing with neural networks. An argument of `None` does nothing. An argument of 'full' does a full greyscaling of the observation. Arguments of 'R','G' or'B' just the corresponding R, G or B color channel from observation, as a dramatically more computationally efficient and generally adequate method of greyscaling games. This is only available for graphical games with 3D outputs.

*Down scaling* uses mean pooling to reduce the observations output by each game by the given x and y scales. The dimension of an environment must be an integer multiple of it's scale. Downscaling is important for making the output of an environment small enough to work with commonly used architectures for deep reinforcement learning. This is only available for graphical games with 2D or 3D outputs. The default is `None`.

*Reshaping* can take argument `flatten`, and turn 2D or 3D observations into a 1D vector, to be usable with simpler neural network architectures. It can also take argument `expand`, which adds an empty dimension to the observation (i.e. turning a 2D array into a 1 tall 3D array).

*Range scaling* linearly scales observations such that env_min is 0 and env_max is 1. This is useful because neural networks generally perform better on normalized inputs, and for example graphical games output observations over (0, 255). The default is `None`.

*New dtypes* turn your observations into a certain dtype when output from the wrapper. This is helpful because, for instance, most graphical games output tensors of `uint8` dtype, while most neural networks require `float32`.

Operations are applied in the order of arguments to the wrapper function.


## Partially Observable Markov Games API

We also include an alternative API and wrapper which can only handle Markov games (of any observability).

Markov games alternate between the environment stepping and all agents stepping simultaneously, and exclude chess for instance. This API assumes the number of agents cannot be changed. This API includes is own base class (`pettingzoo.MarkovEnv`), and so games could be made to comply only with it, though none in this library do this.

This is primarily included for compatibility with many existing MARL code bases (notably RLlib). However, making environments which comply to this API only can allow for a little more parallelization. When working with tens thousands of agents, this may be important.

Using it looks like this:

```
from petttingzoo.utils import markov_game
env = markov_game(env)
observations = env.reset()
while True:
    actions = policy(actions)
    # add env.render() here if you want to watch the game playing and the game supports it
    observations, rewards, dones, info = env.step(actions)
```

This can combined with the observation wrapper in the order `markov_game(wrapper(env))`.

The differences from the AEC environment API are as follows:

*`agent_order`, `agent_selection` and `observe(agent)` are not included.

* Reset and step also do not include their additional flags.

* `dones` also has an `__all__` entry, which is set to be 

*The `observations` and `actions` properties are added, which look very similar to `rewards`, etc.:

```
observations = {0:[first agent's observation], 1:[second agent's observation] ... n-1:[nth agent's observation]}
actions = {0:[first agent's action], 1:[second agent's action] ... n-1:[nth agent's action]}
```


## Other Utils

Additionally, we have a basic test to check for environment compliance, if you've made your own custom environment with PettingZoo and want to get a good guess about whether or not you did it right.

```
from pettingzoo.utils import children
children(env, save_image_observations=False)
```

Set `save_image_observations=True` if you want to save all of the observations of the first 2 steps of environment to disk as .png files, in the directory in which you run this command. This is very helpful in debugging graphical environments. 


## Demos

Often, you want to be able to play a game or watch it play to get an impression of how it works before trying to learn it. Only games with a graphical output, or certain vector output games with a visualization added, can be rendered. 

Of the games that can be played, many can be played by humans, and functionality to do so is included.

```
from pettingzoo.gamma import pistonball
pistonball.manual_control([environment specs])
```

For viewable games that can't be played by humans, you easily can get an impression for them by watching a random policy control all the actions, via:

```
from pettingzoo.utils import random_demo
random_demo(env)
```


## OS Support

We support Linux and macOS, and conduct CI testing on Linux. We will accept PRs related to windows, but do not officially support it. We're open to help adding macOS CI and proper Windows support/CI.

## Further Documentation
For more detailed documentation about all the different environments, and a leader board for each, go to [website].

If you'd like to be listed on the leader board for your environment, please submit a pull request. Only pull requests that link to code for reproducibility will be accepted. You must also use the default environment parameters.

# Creating Custom Environments
Creating a custom environment with PettingZoo should roughly look like the following:

```
import pettingzoo
from gym import spaces


class env(pettingzoo.AECEnv):
    metadata = {'render.modes': ['human']} # only add if environment supports rendering

    def __init__(self, arg1, arg2, ...):
        super(env, self).__init__()

        agents = [0, 1 ... n] # agent names
        agent_order = # list of agent names in the order they act in a cycle. Usuallly this will be the same as the agents list.
        observation_spaces = # dict of observation spaces for each agent, from gym.spaces
        action_spaces = # dict of action spaces for each agent, from gym.spaces
        rewards = {0:[first agent's reward], 1:[second agent's reward] ... n-1:[nth agent's reward]}
        dones = {0:[first agent's done state], 1:[second agent's done state] ... n-1:[nth agent's done state]}
        infos = {0:[first agent's info], 1:[second agent's info] ... n-1:[nth agent's info]}

        # agent selection stuff (Ananth)

        # Initialize game stuff

    def observe(self, agent):
        # return observation of an agent
        return observation

    def step(self, action, observe=True):
        # Do game stuff
        # Switch selection to next agents (Ananth)
        if observe:
            return self.observe(self.agent_selection)
        else:
            return

    # last_cycle is added as a part of the AECEnv class, don't write it yourself

    def reset(self, observe=True):
        # reset environment
        if observe:
            return self.observe(agent_order[0])
        else:
            return

    def render(self, mode='human'): # not all environments will support rendering
        ...

    def close (self): # not all environments will support rendering
        ...
```

## Development Stuff:

All environment code should be compliant with flake8 --ignore E501,E731,E741. We're open to adding more exceptions at this time if needed.

The following environments should be done:

* gamma/prison
* mpe/*

The following environments are done but require porting:

* gamma/knights_archers_zombies (needs AEC API port) (needs wrapper API port) (Mario)
* gamma/pistonball (needs AEC API port) (needs wrapper API port) (Mario)
* gamma/cooperative_pong (needs AEC API port) (needs wrapper API port) (Ananth)
* sisl/* (needs AEC API port) (needs wrapper API port) (Mario)
* classic/rock_paper_scissors (needs AEC API port) (Sharry)

The following games are under active development:

* gamma/prospector (Mario)
* classic/go (Sharry)
* classic/rock_paper_scissors_lizard_spock (Sharry)
* classic/checkers (Tianchen)
* classic/mahjong (rlcard) (Luis)
* classic/texasholdem (rlcard) (Luis)
* classic/texasholdem_nolimit (rlcard) (Luis)
* classic/uno (rlcard) (Luis)
* class/chess (Ben)
* classic/tictactoe (Praveen)
* classic/connect_four (Praveen)

Development has not yet started on the following games:
* magent/*
* classic/backgammon
* atari/*
* robotics/*

Future wrapper work:
"action_cropping and obs_padding implement the techniques described in *Parameter Sharing is Surprisingly Useful for Deep Reinforcement Learning* to standardized heterogeneous action spaces."


Requirements are being kept below until we get the requirements.txt issues fixed

```
gym>=0.15.4
pygame==2.0.0.dev6
scikit-image>=0.16.2
numpy>=1.18.0
matplotlib>=3.1.2
pymunk>=5.6.0
gym[box2d]>=0.15.4
python-chess
```
