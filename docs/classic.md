## Clasic Environments

| Environment                      | Observations | Actions | Agents | Manual Control | Action Shape | Action Values | Observation Shape | Observation Values | Num States |
|----------------------------------|--------------|---------|--------|----------------|--------------|---------------|-------------------|--------------------|------------|
| Backgammon                       | ?            | ?       | ?      | ?              | ?            | ?             | ?                 | ?                  | ?          |
| Checkers                         | ?            | ?       | ?      | ?              | ?            | ?             | ?                 | ?                  | ?          |
| Chess                            | ?            | ?       | ?      | ?              | ?            | ?             | ?                 | ?                  | ?          |
| Connect Four                     | ?            | ?       | ?      | ?              | ?            | ?             | ?                 | ?                  | ?          |
| Dou Dizhu                        | ?            | ?       | ?      | ?              | ?            | ?             | ?                 | ?                  | ?          |
| Gin Rummy                        | ?            | ?       | ?      | ?              | ?            | ?             | ?                 | ?                  | ?          |
| Go                               | ?            | ?       | ?      | ?              | ?            | ?             | ?                 | ?                  | ?          |
| Leduc Hold'em                    | ?            | ?       | ?      | ?              | ?            | ?             | ?                 | ?                  | ?          |
| Mahjong                          | ?            | ?       | ?      | ?              | ?            | ?             | ?                 | ?                  | ?          |
| Rock Paper Scissors              | ?            | ?       | ?      | ?              | ?            | ?             | ?                 | ?                  | ?          |
| Rock Paper Scissors Lizard Spock | ?            | ?       | ?      | ?              | ?            | ?             | ?                 | ?                  | ?          |
| Texas Hold'em                    | ?            | ?       | ?      | ?              | ?            | ?             | ?                 | ?                  | ?          |
| Texas Hold'em No Limit           | ?            | ?       | ?      | ?              | ?            | ?             | ?                 | ?                  | ?          |
| Tic Tac Toe                      | ?            | ?       | ?      | ?              | ?            | ?             | ?                 | ?                  | ?          |
| Uno                              | ?            | ?       | ?      | ?              | ?            | ?             | ?                 | ?                  | ?          |

`pip install pettingzoo[classic]`

*General notes on environments*

### Rock Paper Scissors

| Observations | Actions    | Agents | Manual Control |
|--------------|------------|--------|----------------|
| Vector            | Discrete |   2    | No             |

`pettingzoo.other_envs.rps`

*blurb*

*arguments*

*about arguments*


### Rock Paper Scissors Lizard Spock

| Observations | Actions    | Agents | Manual Control |
|--------------|------------|--------|----------------|
|  Vector      | Discrete   | 2 | No             |

`pettingzoo.other_envs.rpsls`

*blurb*

*arguments*

*about arguments*

### Chess

| Observations | Actions    | Agents | Manual Control |
|--------------|------------|--------|----------------|
|  Graphical      | Discrete[*](#chess-action-space)   | 2 | No             |

`pettingzoo.classic.chess`

Chess is the game studied by AI researches for the longest time, however, it was old solved successfully by machine learning methods by AlphaZero chess in 2016.

This environment's observation and action space are designed to be compatible with AlphaZero chess's observation and action space, however, there are some differences.

#### Chess observation space

Like AlphaZero, the observation space is an 8x8 image representing the board. It has a number of with channels representing:

* Each piece type and player combination. So there is a specific channel that represents your knights. If your knight is in that location, that spot is a 1, otherwise, 0.
* castling rights
* En-passant possibilities are represented by the pawn being on first row instead of the 4th (from the player who moved the pawn's perspective)
* Whether you are black or white
* Whether position has been seen before (2-fold repetition)
* A move clock counting up to the 50 move rule. Represented by a single channel where the *n* th element in the flattened channel is set if there has been *n* moves

Like AlphaZero, the board is always oriented towards the current agent (your king starts on the first row). So the two players are looking at mirror images of the board, not the same board.

Unlike AlphaZero, the observation space does not stack the observations of the 8 or so previous moves by default. If you want to stack this history into the observation, use the observation wrapper's frame stacking method like this:

```
HISTORY_LEN = 8
env = chess.env()
env = wrapper(env, frame_stacking=HISTORY_LEN)
```

#### Chess action space

The chess action space is discrete, but it is also compatible with AlphaZero's policy space. In particular, it is a 8×8×73 = 4672 discrete space that corresponds to a 8×8 image with 73 channels.

Description copied from AlphaZero paper (note that directions are not necessarily in the order specified).

>> action space is a 8x8x73 dimensional array.
Each of the 8×8
positions identifies the square from which to “pick up” a piece. The first 56 planes encode
possible ‘queen moves’ for any piece: a number of squares [1..7] in which the piece will be
moved, along one of eight relative compass directions {N, NE, E, SE, S, SW, W, NW}. The
next 8 planes encode possible knight moves for that piece. The final 9 planes encode possible
underpromotions for pawn moves or captures in two possible diagonals, to knight, bishop or
rook respectively. Other pawn moves or captures from the seventh rank are promoted to a
queen
