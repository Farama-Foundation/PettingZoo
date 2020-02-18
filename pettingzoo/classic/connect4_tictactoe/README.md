#https://github.com/kirarpit/connect4

# Solving board games like Connect4 using RL
This repository contains implementation of multiple Reinforcement Learning(RL) algorithms in which an Artificial Neural Net(ANN) is trained to play board games like Connect4 and TicTacToe. Another purpose of this repository is to gain a comprehensive intuition on how different RL algorithms work, their pros and cons, and the ways in which they differ from each other. Hence, to support experimentation via tweaking hyper-parameters, a general RL framework is implemented with highly customisable modules.

## How it works
- First, a game object is created with arguments like board_size.
- Next, two player objects are created which will play against each other. Every player object has its default brain which could be overridden by creating a custom brain object and assigning it to the player. Brain object is the place where the algorithms reside.
- Next, an environment object is created and two players along with the game objects are put in this environment by passing them as arguments.
- Finally, this environment is run which runs the game, takes actions from the players, and sends them back next state of the game and rewards of their actions.

## How to run
- Git clone this repository.
- Change directory to 'src' folder.
- Add the src folder in PYTHONPATH environment variable.  
`export PYTHONPATH=/path/to/src/folder:$PYTHONPATH`
- Run examples. For example to train a DDQN player learn TicTacToe while playing against a Minimax player, run the below command.  
`python3 examples/T3-DDQNvsMinimax.py`

## Implemented Algorithms
Two main classes of Reinforcement Learning, i.e., Q-Network and Policy Gradient, plus the new self learning algorithm described in AlphaGo Zero<sup id="a1">[1](#fn1)</sup>.
- Deep Q-Network(DQN)<sup id="a2">[2](#fn2)</sup> with Prioritised Experience Replay, reward and error clipping, and a separate target network aka Double DQN. By changing the neural net architecture, even Duelling DQN<sup id="a3">[3](#fn3)</sup> can also be constructed. For more information on DQNs, I suggest this amazing series of [blog posts](https://jaromiru.com/). Few code snippets were directly taken from there.
- Policy Gradient(PG), Asynchronous Advantageous Actor-Critic<sup id="a4">[4](#fn4)</sup> (A3C).
- Asynchronous DQN.
- Possible other variations<sup id="a5">[5](#fn5)</sup> can also be implemented by tweaking the code a bit.
- AlphaGo Zero self learning algorithm implemented down to every detail as described in the methods section of the paper.

## Features
- A model could be trained by playing against a MiniMax player using any of the implemented RL algorithms.
- A model could be trained by self-playing using the AlphaZero or DQN algorithms.
- Convolutional and Residual Layers could simply be toggled with a flag.
- Other similar board games like Gomoku could easily be implemented by extending the base class "Game".

## Players
Every player must implement 'act', 'observe' and 'train' methods of the abstract base class "Player", as these methods would be called by the environment.
- DQN
- PG
- AlphaZero
- MiniMax players for Connect4 and TicTacToe with customisable board size. For Connect4 MiniMax agent on a different board size one must compile one of these repositories [[1]](https://github.com/kirarpit/connect4-minimax), [[2]](https://github.com/MarkusThill/Connect-Four) from source, run them in the background and query them live. Feel free to raise an issue in case you need help with that. For the regular board size, the code will hit an API server which runs the first  repository code mentioned here.
- Human player for playing against trained models.

## Results
- Below are some of the charts showing total wins for player 1(p1), player 2(p2) and draws per 100 games on the Y-axis vs total number of games on the X-axis.
- Post training, all the models shown below for TicTacToe and Connect4 on a smaller board size of 4X5, were able to defeat a corresponding perfect playing Minimax player -- with 5% chance of making a random move each turn -- in 95% of the games.
- For Connect4(regular board size, i.e., 6X7) these algorithms take significant amount of time to train. Parallel processing is not very helpful in python. A model trained for 5 days using AlphaZero algorithm produced strong amateur player.

| ![AlphaZero Player self learning TicTacToe](images/t3-Zero.png)  | ![Async DQN Player vs Minimax on TicTacToe](images/t3-ADQN.png) |
|:---:|:---:|
| AlphaZero Player self learning TicTacToe | Async DQN Player vs Minimax on TicTacToe |

| ![Double DQN Player vs Minimax on TicTacToe](images/t3-DDQN.png)  | ![Policy Gradient Player vs Minimax on TicTacToe](images/t3-PG.png) |
|:---:|:---:|
| Double DQN Player vs Minimax on TicTacToe | Policy Gradient Player vs Minimax on TicTacToe |

| ![Async DQN Player vs Minimax on Connect4(Board size 4X5)](images/C4-4X5-ADQN.png)  | ![Double DQN Player vs Minimax on Connect4(Board size 4X5)](images/C4-4X5-DDQN.png) |
|:---:|:---:|
| Async DQN Player vs Minimax on Connect4(Board size 4X5) | Double DQN Player vs Minimax on Connect4(Board size 4X5) |

| ![Policy Gradient Player vs Minimax on Connect4(Board size 4X5)](images/C4-4X5-PG.png) | ![AlphaZero Player self learning Connect4(Board size 6X7)](images/C4-6X7-Zero.png) |
|:---:|:---:|
| Policy Gradient Player vs Minimax on Connect4(Board size 4X5) | AlphaZero Player self learning Connect4(Board size 6X7) |

## Observations
- Exploration plays a very crucial role in learning. I highly recommend reading more on incentivising exploration<sup id="a6">[6](#fn6)</sup>. Although, due to time constraint I was not able to implement it but it seems promising.
- Getting rewards time to time is crucial for learning. Sparse rewards in such board games where the model receives a reward only at the end of the game, makes learning a lot more difficult and time consuming. One of the remedies is the N_STEP solution. Check PG and Q Players for more info.
- Convolutional networks do perform better because they exploit the spatial representation of the pixels and hence can identify patterns easily.
- DQN can learn from others experiences as well since it can learn offline compared to PG which only learns online. However, PG gives better results since it optimises directly on the policy.
- Asynchronous DQN is most data efficient since a lot more training is going on with every step.
- Asynchronous algorithms work a lot better with workers having different exploration rates since it de-correlates the agent's data and explores the environment faster.
- AlphaZero is definitely a much superior algorithm and generates much better models which outperform other models generated by other mentioned Algorithms. However, it's less general and depends on perfect information assumption.

# Conclusion
This turned out to be a good summer project which gave me a lot of insight into how deep RL algorithms work. I hope newcomers don't have to spend too much time on understanding, implementing and debugging these algorithms by taking advantage of this repository. Feel free to fork, create an issue if there is something you don't understand or make a pull request!

# References
<a name="fn1">1</a>: ["Mastering the game of Go without human knowledge"](https://www.nature.com/articles/nature24270). [↩](#a1)  
<a name="fn2">2</a>: ["Playing Atari with Deep Reinforcement Learning"](https://arxiv.org/abs/1312.5602). [↩](#a2)  
<a name="fn3">3</a>: ["Dueling Network Architectures for Deep Reinforcement Learning"](https://arxiv.org/abs/1511.06581). [↩](#a3)  
<a name="fn4">4</a>: ["Asynchronous Methods for Deep Reinforcement Learning"](https://arxiv.org/abs/1602.01783). [↩](#a4)  
<a name="fn5">5</a>: ["Rainbow: Combining Improvements in Deep Reinforcement Learning"](https://arxiv.org/abs/1710.02298). [↩](#a5)  
<a name="fn6">6</a>: ["Incentivizing Exploration In Reinforcement Learning With Deep Predictive Models"](https://arxiv.org/abs/1507.00814). [↩](#a6)
