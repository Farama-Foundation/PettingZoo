## Classic Environments

| Environment                                             | Actions  | Agents | Manual Control | Action Shape   | Action Values  | Observation Shape | Observation Values |
|---------------------------------------------------------|----------|--------|----------------|----------------|----------------|-------------------|--------------------|
| [Backgammon](classic/backgammon)                        | Discrete | 2      | No             | Discrete(1353) | Discrete(1353) | (198,)            | [0, 7.5]           |
| [Chess](classic/chess)                                  | Discrete | 2      | No             | Discrete(4672) | Discrete(4672) | (8,8,20)          | [0, 1]             |
| [Connect Four](classic/connect_four)                    | Discrete | 2      | No             | Discrete(7)    | Discrete(7)    | (6, 7, 2)         | [0, 1]             |
| [Dou Dizhu](classic/dou_dizhu)                          | Discrete | 3      | No             | Discrete(309)  | Discrete(309)  | (6, 5, 15)        | [0, 1]             |
| [Gin Rummy](classic/gin_rummy)                          | Discrete | 2      | No             | Discrete(110)  | Discrete(110)  | (5, 52)           | [0, 1]             |
| [Go](classic/go)                                        | Discrete | 2      | No             | Discrete(170)  | Discrete(170)  | (170, 170, 3)     | [0, 1]             |
| [Hanabi](classic/hanabi)                                | Discrete | 2      | No             | Discrete(14)   | Discrete(14)   | (373,)            | [0, 1]             |
| [Leduc Hold'em](classic/leduc_holdem)                   | Discrete | 2      | No             | Discrete(4)    | Discrete(4)    | (36,)             | [0, 1]             |
| [Mahjong](classic/mahjong)                              | Discrete | 4      | No             | Discrete(38)   | Discrete(38)   | (6, 34, 4)        | [0, 1]             |
| [Rock Paper Scissors](classic/rps)                      | Discrete | 2      | No             | Discrete(3)    | Discrete(3)    | Discrete(4)       | Discrete(4)        |
| [Rock Paper Scissors Lizard Spock](classic/rpsls)       | Discrete | 2      | No             | Discrete(5)    | Discrete(5)    | Discrete(6)       | Discrete(6)        |
| [Texas Hold'em](classic/texas_holdem)                   | Discrete | 2      | No             | Discrete(4)    | Discrete(4)    | (72,)             | [0, 1]             |
| [Texas Hold'em No Limit](classic/texas_holdem_no_limit) | Discrete | 2      | No             | Discrete(103)  | Discrete(103)  | (54,)             | [0, 100]           |
| [Tic Tac Toe](classic/tictactoe)                        | Discrete | 2      | No             | Discrete(9)    | Discrete(9)    | (3, 3, 2)         | [0, 1]             |
| [Uno](classic/uno)                                      | Discrete | 2      | No             | Discrete(61)   | Discrete(61)   | (7, 4, 15)        | [0, 1]             |


`pip install pettingzoo[classic]`

Classic environments represent implementations of popular turn based human games and are mostly competitive. The classic environments have a few differences from others in this library:

* No classic environments currently take any environment arguments
* All classic environments are rendered solely via printing to terminal
* Many classic environments have illegal moves in the action space, and describe legal moves in  `env.infos[agent]['legal_moves']`. In environments that use this, taking an illegal move will give a reward of -1 to the illegally moving player and 0 to the other players before ending the game. Note that this list is only well defined right before the agents takes its step.
* Reward for most environments only happens at the end of the games once an agent wins or looses, with a reward of 1 for winning and -1 for loosing.

Many environments in classic are based on [RLCard](https://github.com/datamllab/rlcard). If you use these libraries in your research, please cite them:

```
@article{zha2019rlcard,
  title={RLCard: A Toolkit for Reinforcement Learning in Card Games},
  author={Zha, Daochen and Lai, Kwei-Herng and Cao, Yuanpu and Huang, Songyi and Wei, Ruzhe and Guo, Junyu and Hu, Xia},
  journal={arXiv preprint arXiv:1910.04376},
  year={2019}
}
```
