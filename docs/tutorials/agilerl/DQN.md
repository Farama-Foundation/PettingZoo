# AgileRL: Implementing DQN - Curriculum Learning and Self-play
This tutorial shows how to train a [DQN](https://agilerl.readthedocs.io/en/latest/api/algorithms/dqn.html) agent on the [connect four](https://pettingzoo.farama.org/environments/classic/connect_four/) classic environment.

This tutorial focuses on two techniques used in reinforcement learning - **curriculum learning** and **self-play**. Curriculum learning refers to training an agent on tasks of increasing difficulty in separate 'lessons'. Imagine you were trying to become a chess world champion. You would not decide to learn to play chess by immediately taking on a grand master - it would be too difficult. Instead, you would practice against people of the same ability as you, improve slowly, and increasingly play against harder opponents until you were ready to compete with the best. The same concept applies to reinforcement learning models. Sometimes, tasks are too difficult to learn in one go, and so we must create a curriculum to guide an agent and teach it to solve our ultimate hard environment.

This tutorial also uses self-play. Self-play is a technique used in competitive reinforcement learning environments. An agent trains by playing against a copy of itself - the opponent - and learns to beat this opponent. The opponent is then updated to a copy of this better version of the agent, and the agent must then learn to beat itself again. This is done repeatedly, and the agent iteratively improves by exploiting its own weaknesses and discovering new strategies.

In this tutorial, self-play is treated as the final lesson in the curriculum. However, these two techniques can be used independently of each other, and with unlimited resources, self-play can beat agents trained with human-crafted lessons through curriculum learning. [The Bitter Lesson](http://incompleteideas.net/IncIdeas/BitterLesson.html) by Richard Sutton provides an interesting take on curriculum learning and is definitely worth consideration from any engineer undertaking such a task. However, unlike Sutton, we do not all have the resources available to us that Deepmind and top institutions provide, and so one must be pragmatic when deciding how they will solve their own reinforcement learning problem. If you would like to discuss this exciting area of research further, please join the AgileRL [Discord server](https://discord.com/invite/eB8HyTA2ux) and let us know what you think!


## What is DQN?
[DQN](https://agilerl.readthedocs.io/en/latest/api/algorithms/dqn.html) (Deep Q-Network) is an extension of Q-learning that makes use of a replay buffer and target network to improve learning stability. For further information on DQN, check out the AgileRL [documentation](https://agilerl.readthedocs.io/en/latest/api/algorithms/dqn.html).

### Can I use it?

|   | Action Space | Observation Space |
|---|--------------|-------------------|
|Discrete  | ✔️           | ✔️                |
|Continuous   | ❌           | ✔️                |


## Environment Setup

To follow this tutorial, you will need to install the dependencies shown below. It is recommended to use a newly-created virtual environment to avoid dependency conflicts.
```{eval-rst}
.. literalinclude:: ../../../tutorials/AgileRL/requirements.txt
   :language: text
```

## Code
### Curriculum learning and self-play using DQN on Connect Four
The following code should run without any issues. The comments are designed to help you understand how to use PettingZoo with AgileRL. If you have any questions, please feel free to ask in the [Discord server](https://discord.com/invite/eB8HyTA2ux).

This is a complicated tutorial, and so we will go through it in stages. The [full code](#full-training-code) can be found at the end of this section. Although much of this tutorial contains content specific to the Connect Four environment, it serves to demonstrate how techniques can be applied more generally to other problems.

### Imports
Importing the following packages, functions and classes will enable us to run the tutorial.
```python
import copy
import os
import random
from collections import deque
from datetime import datetime

import numpy as np
import torch
import wandb
import yaml
from agilerl.components.replay_buffer import ReplayBuffer
from agilerl.hpo.mutation import Mutations
from agilerl.hpo.tournament import TournamentSelection
from agilerl.utils.utils import initialPopulation
from tqdm import trange

from pettingzoo.classic import connect_four_v3
```

### Curriculum Learning
First, we need to set up and modify our environment to enable curriculum learning. Curriculum learning is enabled by changing the environment that the agent trains in. This can be implemented by changing what happens when certain actions are taken - altering the next observation returned by the environment, or more simply by altering the reward. First, we will change the reward. By default, Connect Four uses the following rewards:

* Win = +1
* Lose = -1
* Play continues = 0

To help guide our agent, we can introduce rewards for other outcomes in the environment, such as a small reward for placing 3 pieces in a row, or a small negative reward when the opponent manages the same feat. We can also use reward shaping to encourage our agent to explore more. In Connect Four, if playing against a random opponent, an easy way to win is to always play in the same column. An agent may find success doing this, and therefore not learn other, more sophisticated strategies that can help it win against better opponents. We may therefore elect to reward vertical wins slightly less than horizontal or diagonal wins, to encourage the agent to try winning in different ways. An example reward system could be defined as follows:

* Win (horizontal or diagonal) = +1
* Win (vertical) = +0.8
* Three in a row = +0.05
* Opponent three in a row = -0.05
* Lose = -1
* Play continues = 0

#### Config files

It is best to use YAML config files to define the lessons in our curriculum and easily change and keep track of our settings. The first two lessons in our curriculum can be defined as follows:

```{eval-rst}
.. literalinclude:: ../../../tutorials/AgileRL/curriculums/connect_four/lesson1.yaml
   :language: yaml
```

```{eval-rst}
.. literalinclude:: ../../../tutorials/AgileRL/curriculums/connect_four/lesson2.yaml
   :language: yaml
```

To implement our curriculum, we create a ```CurriculumEnv``` class that acts as a wrapper on top of our Connect Four environment and enables us to alter the reward to guide the training of our agent. This uses the configs that we set up to define the lesson.

```python

```

When defining the different lessons in our curriculum, we can increase the difficulty of our task by modifying environment observations for our agent - in Connect Four, we can increase the skill level of our opponent. By progressively doing this, we can help our agent improve. We can change our rewards between lessons too; for example, we may wish to reward wins in all directions equally once we have learned to beat a random agent and now wish to train against a harder opponent. In this tutorial, an ```Opponent``` class is implemented to provide different levels of difficulty for training our agent.

```python

```

### General setup

Before we go any further in this tutorial, it would be helpful to define and set up everything remaining we need for training.

```python

```

As part of the curriculum, we may choose to fill the replay buffer with random experiences, and also train on these offline.

```python
```

### Self-play

In this tutorial, we use self-play as the final lesson in our curriculum. By iteratively improving our agent and making it learn to win against itself, we can allow it to discover new strategies and achieve higher performance. The weights of our pretrained agent from an earlier lesson can be loaded to the population as follows:
```python

```

To train against an old version of our agent, we create a pool of opponents. At training time, we randomly select an opponent from this pool. At regular intervals, we update the opponent pool by removing the oldest opponent and adding a copy of the latest version of our agent. This provides a balance between training against an increasingly difficult opponent and providing variety in the moves an opponent might make.

```python

```

### Training loop

The Connect Four training loop must take into account that the agent only takes an action every other interaction with the environment (the opponent takes alternating turns). This must be considered when saving transitions to the replay buffer. Equally, we must wait for the outcome of the next player's turn before determining what the reward should be for a transition. This is not a true Markov Decision Process for this reason, but we can still train a reinforcement learning agent reasonably successfully in these non-stationary conditions.

At regular intervals, we evaluate the performance, or 'fitness',  of the agents in our population, and do an evolutionary step. Those which perform best are more likely to become members of the next generation, and the hyperparameters and neural architectures of agents in the population are mutated. This evolution allows us to optimize hyperparameters and maximise the performance of our agents in a single training run.

```python
```


### Watch the trained agents play
The following code allows you to load your saved DQN agent from the previous training block, test the agent's performance, and then visualise a number of episodes as a gif.
```{eval-rst}
.. literalinclude:: ../../../tutorials/AgileRL/render_agilerl_dqn.py
   :language: python
```

### Full training code

```{eval-rst}
.. literalinclude:: ../../../tutorials/AgileRL/agilerl_dqn_curriculum.py
   :language: python
```
