## Classic Environments

| Environment                                                | Actions  | Agents | Manual Control | Action Shape           | Action Values           | Observation Shape | Observation Values | Num States    |
|------------------------------------------------------------|----------|--------|----------------|------------------------|-------------------------|-------------------|--------------------|---------------|
| [Backgammon](classic/backgammon.md)                        | Discrete | 2      | No             | Discrete(26^2 * 2 + 1) | Discrete( 26^2 * 2 + 1) | (198,)            | [0, 7.5]           | 10^26         |
| [Chess](classic/chess.md)                                  | Discrete | 2      | No             | Discrete(4672)         | Discrete(4672)          | (8,8,20)          | [0, 1]             | ?             |
| [Connect Four](classic/connect_four.md)                    | Discrete | 2      | No             | Discrete(7)            | Discrete(7)             | (6, 7, 2)         | [0, 1]             | ?             |
| [Dou Dizhu](classic/dou_dizhu.md)                          | Discrete | 3      | No             | Discrete(309)          | Discrete(309)           | (6, 5, 15)        | [0, 1]             | 10^53 - 10^83 |
| [Gin Rummy](classic/gin_rummy.md)                          | Discrete | 2      | No             | Discrete(110)          | Discrete(110)           | (5, 52)           | [0, 1]             | 10^52         |
| [Go](classic/go.md) (N=board size)                         | Discrete | 2      | No             | Discrete(N^2+1)        | Discrete(N^2+1)         | (N, N, 3)         | [0, 1]             | 3^(N^2)       |
| [Hanabi](classic/hanabi.md)                                | Discrete | 2      | No             | Discrete(14)           | Discrete(14)            | (373,)            | [0, 1]             | ?             |
| [Leduc Hold'em](classic/leduc_holdem.md)                   | Discrete | 2      | No             | Discrete(4)            | Discrete(4)             | (36,)             | [0, 1]             | 10^2          |
| [Mahjong](classic/mahjong.md)                              | Discrete | 4      | No             | Discrete(38)           | Discrete(38)            | (6, 34, 4)        | [0, 1]             | 10^121        |
| [Rock Paper Scissors](classic/rps.md)                      | ?        | ?      | ?              | ?                      | ?                       | ?                 | ?                  | ?             |
| [Rock Paper Scissors Lizard Spock](classic/rpsls.md)       | ?        | ?      | ?              | ?                      | ?                       | ?                 | ?                  | ?             |
| [Texas Hold'em](classic/texas_holdem.md)                   | Discrete | 2      | No             | Discrete(4)            | Discrete(4)             | (72,)             | [0, 1]             | 10^14         |
| [Texas Hold'em No Limit](classic/texas_holdem_no_limit.md) | Discrete | 2      | No             | Discrete(103)          | Discrete(103)           | (54,)             | [0, 100]           | 10^162        |
| [Tic Tac Toe](classic/tictactoe.md)                        | Discrete | 2      | No             | Discrete(9)            | Discrete(9)             | (3, 3, 2)         | [0, 1]             | ?             |
| [Uno](classic/uno.md)                                      | Discrete | 2      | No             | Discrete(61)           | Discrete(61)            | (7, 4, 15)        | [0, 1]             | 10^163        |


`pip install pettingzoo[classic]`

Classic environments represent implementations of popular turn based human games, and are mostly competitive. The classic environments have a few differences from others in this library:

* No classic environments currently take any environment arguments
* All classic environments are rendered solely via printing to terminal
* Many classic environments have illegal moves in the action space, and describe legal moves in  `env.infos[agent]['legal_moves']`. In environments that use this, taking an illegal move will give a reward of -1 to the illegally moving player, 0 to the other players, and end the game. Note that this list is only well defined right before the agent's takes its step.
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
