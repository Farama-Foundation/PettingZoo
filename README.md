# PettingZoo
PettingZoo is Python library of environments for conducting research in multi-agent reinforcement learning. It's basically a multi-agent version of OpenAI's Gym library.


## Environment Types and Installation

PettingZoo breaks its games down into several categories, largely including games from other's which we've ported to our consistent API, in many cases fixed, and centrally distribute.

* atari: A collection of easily runnable multi-player Atari games in the Stella emulator, similar to what you find in Gym.
* classic: Environments for classical games that two humans play against each other (rock paper scissors, chess, Texas hold 'em poker, go, etc.)
* gamma: Graphical games developed by us, in PyGame. All games are cooperative, and many pose features very challenging to reinforcement learning.
* magent: A set of environments involving massive numbers of agents doing various tasks, originally from https://github.com/geek-ai/MAgent
* mpe: 'Multi-agent Particle Environments', a set of simple nongraphical communication tasks created by OpenAI: https://github.com/openai/multiagent-particle-envs
* robotics: A collection of 3D multi-agent robot environments, simulated with MuJoC
* sisl: An eclectic collection of 3 games developed by SISL, originally from https://github.com/sisl/MADRL

To install a set of games, use `pip3 install pettingzoo[atari]`, substituting atari for other classes of games when desired.

We support Python 3.6, 3.7 and 3.8.


## Initializing Environments

Using environments in PettingZoo is very similar to Gym, i.e. you initialize an environment via:

```
from pettingzoo.gamma import pistonball
env = pistonball.env()
```

Environments are all easily highly configurable, so that the effects of different unique environmental parameters on multi-agent learning can be more easily studied. This is done in the form optional arguments based to the environment when it's created. For example:

```
cooperative_pong.env(ball_velocity=?, left_paddle_velocity=?,
right_paddle_velocity=?, wedding_cake_paddle=True, max_frames=900)
```


## Simple Environment Interactions
Games can be interacted with as follows in the simplest case, in a manner very similar to Gym: 

```
first_observation = env.reset()
while True:
    for agent in env.agents:
        action = policy(agent,env.observe(agent))) # this could also be cached from last the observation that agent took
        observation, reward, done, info = env.step(action) # control shifts to next agent
```

For games where the instant observations or reward are undesired (or other interesting things are happening), you must make additional calls to the full API.


## Full Environment API

PettingZoo fundamentally models environments as *Agent Environment Cycle* (AEC) games, because they can handle any environment considerable by RL (including single agent).

PettingZoo environments have the following attributes:

`env.agents`: A list of the names of all current agents, typically integers. These may be changed as an enviroment progresses (i.e. agents can be added or removed).

`env.agent_order`: A list of the order agents take turns in. The 0th element of the list acts first, and so on.

`env.observation_spaces`: A dict of the gym observation spaces of every agent, by name.

`env.action_spaces`: A dict of the gym action spaces of every agent, by name.

`env.rewards`: A dict of the rewards of every agent at the time called, by name. This can generally be changed at any point in the metaenvironment portion of the AEC cycle, and so isn't guaranteed to be "final" until the agent's turn is reached again.

`env.dones`: A dict of the done state of every agent at the time called, by name. This can generally be changed at any point in the metaenvironment portion of the AEC cycle, and so isn't guaranteed to be "final" until the agent's turn is reached again.

`env.infos`: A dict of info for each agent, by name. Included for extensibility, and because info is a part of the Gym API. All games built into this repo only output '' for each agent.

`env.agent_selection`: Gives name of agent currently poised to be acted on.

Our AEC environments have the following methods:

`env.observe(agent)`: Returns the observation an agent currently can make.

`env.turn(action=None)`: Has the selected agent take a turn, selects the next agent. In AEC games, after every agent takes a turn a step is said to have been taken. Taking turns with `action=None` can be used to cycle through turns of the environment if desired.

`env.reset(observe=True)`: Resets the environment to a starting state. Returns the observation for the first moving agent in the environment if `observe=True`.

`env.render()`: Displays a rendered frame from the environment, if supported.

`env.close()`: Closes the rendering window.

`env.step(actions)`: Makes calls to other parts of the API to take a Gym like step in the environment, returning the observation, reward, done state and info for the selected agent in the environment. Control shifts to next agent. This is different than the notion of a step in an AEC game.


## Wrapper API

We include popular preprocessing methods out of the box:

```
from pettingzoo.utils import wrapper
env = wrapper(env, color_reduction=None, down_scale=(x_scale, y_scale), reshape=None,
range_scale=(obs_min, obs_max), new_dtype=None, frame_stacking=1)
```

*Frame stacking* stacks the 4 most recent frames on "top of" each other. For vector games observed via plain vectors (1D arrays), the output is just concatenated to a longer 1D array. For games via observed via graphical outputs (a 2D or 3D array), the arrays are stacked to be taller 3D arrays. Frame stacking is used to let policies get a sense of time from the environments. The argument to frame stacking controls how many frames back are stacked. At the start of the game, frames that don't yet exist are filled with 0s. An argument of 1 is analogous to being turned off.

*Color reduction* removes color information from game outputs to easier processing with neural networks. An argument of `None` does nothing. An argument of 'full' does a full greyscaling of the observation. Arguments of 'R','G' or'B' just the corresponding R, G or B color channel from observation, as a dramatically more computationally efficient and generally adequate method of greyscaling games. This is only available for graphical games with 3D outputs.

*Down scaling* uses mean pooling to reduce the observations output by each game by the given x and y scales. The dimension of an environment must be an integer multiple of it's scale. Downscaling is important for making the output of an environment small enough to work with commonly used architectures for deep reinforcement learning. This is only available for graphical games with 2D or 3D outputs. The default is `None`.

*Reshapping* can take argument `flatten`, and turn 2D or 3D observations into a 1D vector, to be usable with simpler neural network architectures. It can also take argument `expand`, which adds an empty dimension to the observation (i.e. turning a 2D array into a 1 tall 3D array).

*Range scaling* linearly scales observations such that env_min is 0 and env_max is 1. This is useful because neural networks generally perform better on normalized inputs, and for example graphical games output observations over (0, 255). The default is `None`.

*New dtypes* turn your observations into a certain dtype when output from the wrapper. This is helpful because, for instance, most graphical games output tensors of `uint8` dtype, while most neural networks require `float32`.

Operations are applied in the order of arguments to the wrapper function.


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
pistonball.manual_control(game.env([environment specs]))
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



## Development stuff:

All game code should be compliant with flake8 --ignore E501,E731,E741. We're open to adding more exceptions at this time if needed.

The following games should be done (though they aren't compliant with the wrapper API yet):

* gamma/knights_archers_zombies
* gamma/pistonball
* gamma/cooperative_pong
* sisl/pursuit
* sisl/multiwalker
* sisl/waterworld
* classic/rock_paper_scissors

The following games are under active development:

* gamma/prospector (Rui)
* gamma/prison (Mario)
* classic/go (Sharry)
* classic/rock_paper_scissors_lizard_spock (Sharry)
* clasic/checkers (Tianchen)
* classic/mahjong (rlcard) (Luis)
* classic/texasholdem (rlcard) (Luis)
* classic/texasholdem_nolimit (rlcard) (Luis)
* classic/uno (rlcard) (Luis)
* mpe/*

Development has not yet started on the following games:

* classic/backgammon
* classic/chess (https://github.com/niklasf/python-chess)
* classic/tictactoe
* classic/connect_four
* magent/*
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
