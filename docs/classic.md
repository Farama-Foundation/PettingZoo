## Classic Environments

| Environment                      | Observations | Actions  | Agents | Manual Control | Action Shape  | Action Values  | Observation Shape | Observation Values | Num States |
|----------------------------------|--------------|----------|--------|----------------|---------------|----------------|-------------------|--------------------|------------|
| Backgammon                       | ?            | ?        | ?      | ?              | ?             | ?              | ?                 | ?                  | ?          |
| Checkers                         | ?            | ?        | ?      | ?              | ?             | ?              | ?                 | ?                  | ?          |
| Chess                            | Graphical    | Discrete | 2      | No             | Discrete(4672) | Discrete(4672) | (8,8,20)          | [0,1]              | ?          |
| Connect Four                     | ?            | ?        | ?      | ?              | ?             | ?              | ?                 | ?                  | ?          |
| Dou Dizhu                        | ?            | ?        | ?      | ?              | ?             | ?              | ?                 | ?                  | ?          |
| Gin Rummy                        | ?            | ?        | ?      | ?              | ?             | ?              | ?                 | ?                  | ?          |
| Go                               | ?            | ?        | ?      | ?              | ?             | ?              | ?                 | ?                  | ?          |
| Leduc Hold'em                    | ?            | ?        | ?      | ?              | ?             | ?              | ?                 | ?                  | ?          |
| Mahjong                          | ?            | ?        | ?      | ?              | ?             | ?              | ?                 | ?                  | ?          |
| Rock Paper Scissors              | ?            | ?        | ?      | ?              | ?             | ?              | ?                 | ?                  | ?          |
| Rock Paper Scissors Lizard Spock | ?            | ?        | ?      | ?              | ?             | ?              | ?                 | ?                  | ?          |
| Texas Hold'em                    | ?            | ?        | ?      | ?              | ?             | ?              | ?                 | ?                  | ?          |
| Texas Hold'em No Limit           | ?            | ?        | ?      | ?              | ?             | ?              | ?                 | ?                  | ?          |
| Tic Tac Toe                      | ?            | ?        | ?      | ?              | ?             | ?              | ?                 | ?                  | ?          |
| Uno                              | ?            | ?        | ?      | ?              | ?             | ?              | ?                 | ?                  | ?          |

`pip install pettingzoo[classic]`

Classic environments represent implementations of popular turn based human games, and are mostly competative. The classic environments have a few differences from others in this library:

* No classic environments currently take any environment arguments
* All classic environments are rendered solely via printing to terminal
* Many classic environments make use of <Ben talk about env.info[agent][legal_moves] here>


### Backgammon

| Observations | Actions | Agents | Manual Control | Action Shape | Action Values | Observation Shape | Observation Values | Num States |
|--------------|----------|---------|----------------|--------------|---------------|-------------------|--------------------|------------|
| ?            | ?       | ?      | ?              | ?            | ?             | ?                 | ?                  | ?          |

`from pettingzoo.classic import backgammon`

*gif*

*AEC Diagram*

*Blurb*

*Env arguments*

*About env arguments*


### Checkers

| Observations | Actions | Agents | Manual Control | Action Shape | Action Values | Observation Shape | Observation Values | Num States |
|--------------|----------|---------|----------------|--------------|---------------|-------------------|--------------------|------------|
| ?            | ?       | ?      | ?              | ?            | ?             | ?                 | ?                  | ?          |

`from pettingzoo.classic import checkers`

*gif*

*AEC Diagram*

*Blurb*

### Chess

| Observations | Actions  | Agents | Manual Control | Action Shape                           | Action Values  | Observation Shape | Observation Values | Num States |
|--------------|----------|--------|----------------|----------------------------------------|----------------|-------------------|--------------------|------------|
| Graphical    | Discrete | 2      | No             | Discrete(4672)[*](#chess-action-space) | Discrete(4672) | (8,8,20)          | [0,1]              | ?          |

`pettingzoo.classic.chess`

*gif*

*AEC Diagram*

Chess is the game studied by AI researches for the longest time, with research dating back to the late 40s. However, it was only solved successfully by machine learning methods by AlphaZero Chess in 2016.

This environment's observation and action space are designed to be very similar to AlphaZero chess's observation and action space, however, there are some slight differences.

#### Observation Space

Like AlphaZero, the observation space is an 8x8 image representing the board. It has a number of with channels representing:

* Each piece type and player combination. So there is a specific channel that represents your knights. If your knight is in that location, that spot is a 1, otherwise, 0.
* Castling rights
* En-passant possibilities are represented by the pawn being on first row instead of the 4th (from the player who moved the pawn's perspective)
* Whether you are black or white
* Whether position has been seen before (2-fold repetition)
* A move clock counting up to the 50 move rule. Represented by a single channel where the *n* th element in the flattened channel is set if there has been *n* moves

Like AlphaZero, the board is always oriented towards the current agent (your king starts on the first row). So the two players are looking at mirror images of the board, not the same board.

Unlike AlphaZero, the observation space does not stack the observations previous moves by default. This can be accomplished using the `frame_stacking` argument of our wrapper.

#### Action Space

From the AlphaChessZero paper:

>> [In AlphaChessZero, the] action space is a 8x8x73 dimensional array.
Each of the 8×8
positions identifies the square from which to “pick up” a piece. The first 56 planes encode
possible ‘queen moves’ for any piece: a number of squares [1..7] in which the piece will be
moved, along one of eight relative compass directions {N, NE, E, SE, S, SW, W, NW}. The
next 8 planes encode possible knight moves for that piece. The final 9 planes encode possible
underpromotions for pawn moves or captures in two possible diagonals, to knight, bishop or
rook respectively. Other pawn moves or captures from the seventh rank are promoted to a
queen.

We instead have a 8×8×73 = 4672 discrete space, that otherwise functions identically to this.

### Dou Dizhu

| Observations | Actions  | Agents | Manual Control | Action Shape | Action Values | Observation Shape | Observation Values | Num States |
|--------------|----------|--------|----------------|--------------|---------------|-------------------|--------------------|------------|
| ?            | Discrete | 3      | No             | (1)          | [0, 308]      | (6, 5, 15)        | [0,1]              | ?          |

`from pettingzoo.classic import dou_dizhu`

*gif*

*AEC Diagram*

Dou Dizhu, or Fighting the Landlord, is a shedding game involving 3 players and a deck of cards plus 2 jokers with suits being irrelevant. Heuristically, one player is designated the "Landlord" and the others become the "Peasants". The objective of the game is to be the first one to have no cards left. If the first person to have no cards left is part of the "Peasant" team, then all members of the "Peasant" team receive a reward (+1). If the "Landlord" wins, then only the "Landlord" receives a reward (+1).

The "Landlord" plays first by putting down a combination of cards. The next player, may pass or put down a higher combination of cards that beat the previous play. There are many legal combinations of cards, which you can check in [Wikipedia](https://en.wikipedia.org/wiki/Dou_dizhu).

Dou Dizhu depends on [RLCard](http://rlcard.org/) and you can refer to its documentation for additional details.

*Env arguments*

*About env arguments*

### Gin Rummy

| Observations | Actions | Agents | Manual Control | Action Shape | Action Values | Observation Shape | Observation Values | Num States |
|--------------|----------|---------|----------------|--------------|---------------|-------------------|--------------------|------------|
| ?            | ?       | ?      | ?              | ?            | ?             | ?                 | ?                  | ?          |

`from pettingzoo.classic import gin_rummy`

*gif*

*AEC Diagram*

*Blurb*

### Go

| Observations | Actions | Agents | Manual Control | Action Shape | Action Values | Observation Shape | Observation Values | Num States |
|--------------|----------|---------|----------------|--------------|---------------|-------------------|--------------------|------------|
| ?            | ?       | ?      | ?              | ?            | ?             | ?                 | ?                  | ?          |

`from pettingzoo.classic import go`

*gif*

*AEC Diagram*

*Blurb*

*Env arguments*

*About env arguments*

### Leduc Hold'em

| Observations | Actions | Agents | Manual Control | Action Shape | Action Values | Observation Shape | Observation Values | Num States |
|--------------|----------|---------|----------------|--------------|---------------|-------------------|--------------------|------------|
| ?            | ?       | ?      | ?              | ?            | ?             | ?                 | ?                  | ?          |

`from pettingzoo.classic import leduc_holdem`

*gif*

*AEC Diagram*

*Blurb*

### Mahjong

| Observations | Actions | Agents | Manual Control | Action Shape | Action Values | Observation Shape | Observation Values | Num States |
|--------------|----------|---------|----------------|--------------|---------------|-------------------|--------------------|------------|
| ?            | ?       | ?      | ?              | ?            | ?             | ?                 | ?                  | ?          |

`from pettingzoo.classic import mahjong`

*gif*

*AEC Diagram*

*Blurb*

### Rock Paper Scissors

| Observations | Actions | Agents | Manual Control | Action Shape | Action Values | Observation Shape | Observation Values | Num States |
|--------------|----------|---------|----------------|--------------|---------------|-------------------|--------------------|------------|
| ?            | ?       | ?      | ?              | ?            | ?             | ?                 | ?                  | ?          |

`from pettingzoo.classic import rps`

*gif*

*AEC Diagram*

*Blurb*

### Rock Paper Scissors Lizard Spock

| Observations | Actions | Agents | Manual Control | Action Shape | Action Values | Observation Shape | Observation Values | Num States |
|--------------|----------|---------|----------------|--------------|---------------|-------------------|--------------------|------------|
| ?            | ?       | ?      | ?              | ?            | ?             | ?                 | ?                  | ?          |

`from pettingzoo.classic import rpsls`

*gif*

*AEC Diagram*

*Blurb*

### Texas Hold'em

| Observations | Actions | Agents | Manual Control | Action Shape | Action Values | Observation Shape | Observation Values | Num States |
|--------------|----------|---------|----------------|--------------|---------------|-------------------|--------------------|------------|
| ?            | ?       | ?      | ?              | ?            | ?             | ?                 | ?                  | ?          |

`from pettingzoo.classic import texas_holdem`

*gif*

*AEC Diagram*

*Blurb*

### Texas Hold'em No Limit

| Observations | Actions | Agents | Manual Control | Action Shape | Action Values | Observation Shape | Observation Values | Num States |
|--------------|----------|---------|----------------|--------------|---------------|-------------------|--------------------|------------|
| ?            | ?       | ?      | ?              | ?            | ?             | ?                 | ?                  | ?          |

`from pettingzoo.classic import texas_holdem_no_limit`

*gif*

*AEC Diagram*

*Blurb*

### Tic Tac Toe

| Observations | Actions | Agents | Manual Control | Action Shape | Action Values | Observation Shape | Observation Values | Num States |
|--------------|----------|---------|----------------|--------------|---------------|-------------------|--------------------|------------|
| ?            | Discrete | 2       | yes            | (1)          | [0, 9]        | (3, 3)            | [0,1,2]            | ?          |

`from pettingzoo.classic import tictactoe`

*gif*

*AEC Diagram*

Tic-tac-toe is a simple turn based strategy game where 2 players, X and O, take turns marking spaces on a 3 x 3 grid. The first player to place 3 of their marks in a horizontal, vertical, or diagonal row is the winner. If played properly by both players, the game will always end in a draw. Check out [Wikipedia](https://en.wikipedia.org/wiki/Tic-tac-toe) for more information.

### Uno

| Observations | Actions | Agents | Manual Control | Action Shape | Action Values | Observation Shape | Observation Values | Num States |
|--------------|----------|---------|----------------|--------------|---------------|-------------------|--------------------|------------|
| ?            | ?       | ?      | ?              | ?            | ?             | ?                 | ?                  | ?          |

`from pettingzoo.classic import uno`

*gif*

*AEC Diagram*

*Blurb*
