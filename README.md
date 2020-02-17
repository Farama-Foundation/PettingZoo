# PettingZoo
PettingZoo is library of enviroments for conducting research in multi-agent reinforcement learning. It's basically a multi-agent version of OpenAI's Gym library.


## Games and Installation

PettingZoo breaks its games down into several categories, largely including games from other's which we've ported to our consistent API, in many cases fixed, and centrally distribute.

* gamma: Graphical games developed by us, in PyGame
* sisl: An eclectic collection of 4 games developed by SISL, originally from https://github.com/sisl/MADRL
* mpe: 'Multi-agent Particle Enviroments', a set of simple nongraphical communication tasks created by OpenAI: https://github.com/openai/multiagent-particle-envs
* magent: A set of enviroments involving massive numbers of agents doing various tasks, originally from https://github.com/geek-ai/MAgent
* card: A set of card games that can be played.
* atari: A collection of easily runnable multi-player Atari games in the Stella emulator, similar to what you find in Gym.
* mujuco: A collection of 3D mujuco enviroments for multiagent robot simulations
* other-envs: A small collection of enviroments that don't fit anywhere else.

To install a set of games, use `pip3 install pettingzoo[atari]`, substituting atari for other classes of games when desired.


## Base API

Using environments in PettingZoo is very similar to Gym, i.e. you would run 

```
from pettingzoo.gamma import pistonball
env = pistonball.env([custom enviroment parameters])
```

The basic functionality is the same as Gym, but plural i.e.:

```
env.reset()
while True:
    actions = policy(actions)
    # add env.render() here if you want to watch the game playing and the game supports it
    observations, rewards, dones, info = env.step(actions)
```

The way we handle multiple agents is that the enviroment assigns each agent an integer ID, and everything is passed as dictionaries with the IDs as keys, i.e.:

```
observations = {0:[first agent's observation], 1:[second agent's observation] ... n:[n-1th agent's observation]}
actions = {0:[first agent's action], 1:[second agent's action] ... n:[n-1th agent's action]}
rewards = {0:[first agent's reward], 1:[second agent's reward] ... n:[n-1th agent's reward]}
dones = {0:[first agent's done state], 1:[second agent's done state] ... n:[n-1th agent's done state]}
```

When some agents are `done` and others are not, the `done` agents don't respond to input, and return 0s for every value of their observation space. 


## Utils API

We include popular preprocessing methods out of the box:

```
from pettingzoo.utils import wrapper
env = wrapper(env,frame_stacking=4, grey_scale=True, downscale=(x_factor,y_factor), flatten=False, action_cropping=False, obs_padding=False)
```

Only games with a graphical observation space can be greyscaled, downscaled, or flattened. action_cropping and obs_padding implement the techniques described in *Parameter Sharing is Surprisingly Useful for Deep Reinforcement Learning* to standardized heterogenous action spaces.

Additionally, we have a basic test to check for enviroment compliance, if you've made your own custom enviroment with PettingZoo and want to get a good guess about whether or not you did it right.

```
from pettingzoo.utils import children
children(env, save_image_observations=False)
```

Set `save_image_observations=True` if you want to save all of the observations of the first 2 steps of enviroment to disk as .png files, in the directory in which you run this command. This is very helpful in debugging graphical enviroments. 

## Demos

Often, you want to be able to play a game or watch it play to get an impression of how it works before trying to learn it. Only games with a graphical output, or certain vector output games with a visualization added, can be rendered. 

Of the games that can be played, many can be played by humans, and functionality to do so is included.

```
from pettingzoo.gamma.pistonball import pistonball
pistonball.manual_control([enviroment specs])
```

For viewable games that can't be played by humans, you easily can get an impression for them by watching a random policy control all the actions, via:

```
from pettingzoo.utils import random_demo
random_demo(env)
```

## Documentation
For more detailed documentation about all the different enviroments, and configuration options for them go to [website].

We maintain a leaderboard for the best performance on every game, included in the documentation for each game. If you have a score that you would like to be included, please submit a pull request. Only pull requests that link to code for reproducibility will be accepted. You must also use the default parameters for every game, with the exception that we 2 have seperate leaderboards for games that support both continuous and discrete action spaces.


## Development Notes

The following games should be done (though haven't been fully reconfigured for the new API):

* gamma/knights_archers_zombies
* gamma/pistonball
* gamma/cooperative_pong
* sisl/pursuit
* sisl/multiwalker
* sisl/waterworld

The following games are under active development:

* gamma/prospector
* gamma/prison (not merged into this repo yet)
* sisl/multiant
* other_envs/rock_paper_scissors
* other_envs/rock_paper_scissors_lizard_spock
* mpe/*

Development has not yet started on the following games:

* magent/*
* atari/*
* card/*
* mujuco/*


## Requirements

Requirements are being kept below until we get the requirments.txt issues fixed

```
gym>=0.15.4	
pygame==2.0.0.dev6	
scikit-image>=0.16.2	
numpy>=1.18.0	
matplotlib>=3.1.2
pymunk>=5.6.0
gym[box2d]>=0.15.4
```


