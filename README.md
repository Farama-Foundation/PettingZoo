# Overview
PettingZoo is library of enviroments for conducting research in multi-agent reinforcement learning. It's basically a multi-agent version of OpenAI's Gym library.

# Games and Installation

PettingZoo breaks it's games down into several categories, largely including games from other's which we've ported to our consistent API, in many cases fixed, and centrally distribute.

* gamma: Graphical games developed by us, in PyGame
* sisl: An ecclectic collection of 4 games developed by SISL, originally from https://github.com/sisl/MADRL
* mpe: 'Multi-agent Particle Enviroments', a set of simple nongraphical communication tasks created by OpenAI: https://github.com/openai/multiagent-particle-envs
* magent: A set of enviroments involving massive numbers of agents doing various tasks, originally from https://github.com/geek-ai/MAgent
* card: A set of card games that can be played.
* atari: A collection of easily runnable multi-player Atari games in the Stella emulator, similar to what you find in Gym.
* other-envs: A small collection of enviroments that don't fit anywhere else.

To install a set of games, use `pip3 install pettingzoo[atari]`, substituting atari for other classes of games when desired.


## API

Using enviroments in PettingZoo is very similar to Gym, i.e. you would run 

`from pettingzoo.gamma import pistonball`

`env = pistonball.([arguments])`

The basic functionality is the same as Gym, but plural i.e.:

```
env.reset()
While True:
    actions = policy(actions)
    # add env.render() here if you want to watch the game playing and the game supports it
    observations, rewards, dones, info = env.step(actions)
```

The way we handle multiple agents, or groups of them, is the the enviroment assigns each an integer ID, and every single agent thing is passed as dictionaries based on those IDs, i.e.

```
observations = {0:[first agents observation], 1:[second agents observation] ... n:[n-1th agents observation]}
actions = {0:[first agents action], 1:[second agents action] ... n:[n-1th agents action]}
rewards = {0:[first agents reward], 1:[second agents reward] ... n:[n-1th agents reward]}
dones = {0:[first agents done state], 1:[second agents done state] ... n:[n-1th agents done state]}
```

## Utils

For games that support manual control, you can run the following script to play the game yourself to try them out:

```
from pettingzoo.utils import manual_control
env = pistonball.([arguments])
manual_control(env)
```

Additionally, we include popular preprocessing methods out of the box:

```
from pettingzoo.utils import wrapper
env = wrapper(env,frame_stacking=4, grey_scale=True, scaling = True)
```

Finally, we have a basic test to check for enviroment compliance, if you've made your own custom enviroment with PettingZoo and want to get a good guess about whether or not you did it right.

```
from pettingzoo.utils import children
children(env)
```

## Documentation
For more detailed documentation about all the different enviroments, and configuration options for them go to [website].

We maintain a leaderboard for the best performance on each dataset with the documentation for each game. If you've beat a high score and would like to be included, please submit a pull request. Only pull requests that link to code for reproducibility will be accepted.
