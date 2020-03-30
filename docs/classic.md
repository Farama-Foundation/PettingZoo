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

Classic environments represent implementations of popular turn based human games, and are mostly competitive. The classic environments have a few differences from others in this library:

* No classic environments currently take any environment arguments
* All classic environments are rendered solely via printing to terminal
* Many classic environments have illegal moves in the action space that, if taken, will end the game as a loss for the player who made the illegal move, and assign zero reward for every other player. If there are any illegal moves in that game, then there is a list of legal moves in the "legal_moves" entry in the info dictionary (e.g. `env.infos[agent]['legal_moves']`). Note that this list is only well defined right before the agent's takes its step.
* Reward for most environments only happens at the end of the games once an agent wins or looses, with a reward of 1 for winning and -1 for loosing.


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
| Graphical    | Discrete | 2      | No             | Discrete(4672) | Discrete(4672) | (8,8,20)          | [0,1]              | ?          |

`pettingzoo.classic.chess`

*gif*

*AEC Diagram*

Chess is one of the oldest studied games in AI. Our implementation of the observation and action spaces for chess are what the AlphaZero method uses, with two small changes.

#### Observation Space

Like AlphaZero, the observation space is an 8x8 image representing the board. It has 20 channels representing:

* First 4 channels: Castling rights:
* Next channel: Is black or white
* Next channel: A move clock counting up to the 50 move rule. Represented by a single channel where the *n* th element in the flattened channel is set if there has been *n* moves
* Next channel: all ones to help neural network find board edges in padded convolutions
* Next 12 channels: Each piece type and player combination. So there is a specific channel that represents your knights. If your knight is in that location, that spot is a 1, otherwise, 0. En-passant possibilities are represented by the pawn being on first row instead of the 4th (from the player who moved the pawn's perspective)
* Finally, a channel representing whether position has been seen before (is a 2-fold repetition)

Like AlphaZero, the board is always oriented towards the current agent (your king starts on the first row). So the two players are looking at mirror images of the board, not the same board.

Unlike AlphaZero, the observation space does not stack the observations previous moves by default. This can be accomplished using the `frame_stacking` argument of our wrapper.

#### Action Space

From the AlphaZero chess paper:

>> [In AlphaChessZero, the] action space is a 8x8x73 dimensional array.
Each of the 8×8
positions identifies the square from which to “pick up” a piece. The first 56 planes encode
possible ‘queen moves’ for any piece: a number of squares [1..7] in which the piece will be
moved, along one of eight relative compass directions {N, NE, E, SE, S, SW, W, NW}. The
next 8 planes encode possible knight moves for that piece. The final 9 planes encode possible
underpromotions for pawn moves or captures in two possible diagonals, to knight, bishop or
rook respectively. Other pawn moves or captures from the seventh rank are promoted to a
queen.

We instead flatten this into 8×8×73 = 4672 discrete action space.

#### Rewards

Rewards are zero until the end of a game. If there is a decisive outcome then the score is +1 for a the winning player, -1 for the losing player. If there is a draw, then both player receive zero reward. Like all classical games, if an illegal move is played, then the player who made the illegal move receives -1 reward, and the other player receives 0 reward (this can be avoided by only choosing moves in the `"legal_moves"` entry in the info dictionary).

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
