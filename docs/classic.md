## Classic Environments

| Environment                      | Observations | Actions  | Agents | Manual Control | Action Shape  | Action Values  | Observation Shape | Observation Values | Num States |
|----------------------------------|--------------|----------|--------|----------------|---------------|----------------|-------------------|--------------------|------------|
| Backgammon                       | ?            | ?        | ?      | ?              | ?             | ?              | ?                 | ?                  | ?          |
| Checkers                         | ?            | ?        | ?      | ?              | ?             | ?              | ?                 | ?                  | ?          |
| Chess                            | Graphical    | Discrete | 2      | No             | Discrete(4672) | Discrete(4672) | (8,8,20)          | [0,1]              | ?          |
| Connect Four                     | ?            | ?        | ?      | ?              | ?             | ?              | ?                 | ?                  | ?          |
| Dou Dizhu                        | Vector       | Discrete | 3      | No             | Discrete(309) | Discrete(309)  | (6, 5, 15)        | [0,1]               | ?          |
| Gin Rummy                        | Graphical    | Discrete | 2      | No             | Discrete(110) | Discrete(110)  | (5, 52)           | [0,1]               | ?          |
| Go                               | ?            | ?        | ?      | ?              | ?             | ?              | ?                 | ?                  | ?          |
| Leduc Hold'em                    | Graphical    | Discrete | 2      | No             | Discrete(4)   | Discrete(4)    | (34,)             | [0, Inf]               | ?          |
| Mahjong                          | Vector       | Discrete | 4      | No             | Discrete(38)  | Discrete(38)   | (6, 34, 4)        | [0, 1]                 | ?          |
| Rock Paper Scissors              | ?            | ?        | ?      | ?              | ?             | ?              | ?                 | ?                  | ?          |
| Rock Paper Scissors Lizard Spock | ?            | ?        | ?      | ?              | ?             | ?              | ?                 | ?                  | ?          |
| Texas Hold'em                    | Graphical    | Discrete | 2      | No             | Discrete(4)   | Discrete(4)    | (72,)             | [0, 1]                 | ?          |
| Texas Hold'em No Limit           | Graphical    | Discrete | 2      | No             | Discrete(103) | Discrete(103)  | (54,)             | [0, 100]               | ?          |
| Tic Tac Toe                      | ?            | ?        | ?      | ?              | ?             | ?              | ?                 | ?                  | ?          |
| Uno                              | Vector       | Discrete | 2      | No             | Discrete(61)  | Discrete(61)   | (7, 4, 15)        | [0, 1]                 | ?          |

`pip install pettingzoo[classic]`

Classic environments represent implementations of popular turn based human games, and are mostly competitive. The classic environments have a few differences from others in this library:

* No classic environments currently take any environment arguments
* All classic environments are rendered solely via printing to terminal
* Many classic environments have illegal moves in the action space that, if taken, will end the game as a loss for the player who made the illegal move, and assign zero reward for every other player. If there are any illegal moves in that game, then there is a list of legal moves in the "legal_moves" entry in the info dictionary (e.g. `env.infos[agent]['legal_moves']`). Note that this list is only well defined right before the agent's takes its step.
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

### Backgammon

| Observations | Actions | Agents | Manual Control | Action Shape | Action Values | Observation Shape | Observation Values | Num States |
|--------------|----------|---------|----------------|--------------|---------------|-------------------|--------------------|------------|
| ?            | ?       | ?      | ?              | ?            | ?             | ?                 | ?                  | ?          |

`from pettingzoo.classic import backgammon`

*gif*

*AEC Diagram*

*Blurb*


### Checkers

| Observations | Actions | Agents | Manual Control | Action Shape | Action Values | Observation Shape | Observation Values | Num States |
|--------------|----------|---------|----------------|--------------|---------------|-------------------|--------------------|------------|
| ?            | ?       | ?      | ?              | ?            | ?             | ?                 | ?                  | ?          |

`from pettingzoo.classic import checkers`

*gif*

*AEC Diagram*

*Blurb*

#### Observation Space

#### Action Space

#### Rewards

| Winner | Loser |
| :----: | ----- |
| +1     | -1    |

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

| Winner | Loser |
| :----: | ----- |
| +1     | -1    |

### Dou Dizhu

| Observations | Actions  | Agents | Manual Control | Action Shape  | Action Values  | Observation Shape | Observation Values | Num States |
|--------------|----------|--------|----------------|---------------|----------------|-------------------|--------------------|------------|
| Vector       | Discrete | 3      | No             | Discrete(309) | Discrete(309)  | (6, 5, 15)        | [0,1]              | ?          |

`from pettingzoo.classic import dou_dizhu`

*gif*

*AEC Diagram*

Dou Dizhu, or *Fighting the Landlord*, is a shedding game involving 3 players and a deck of cards plus 2 jokers with suits being irrelevant. Heuristically, one player is designated the "Landlord" and the others become the "Peasants". The objective of the game is to be the first one to have no cards left. If the first person to have no cards left is part of the "Peasant" team, then all members of the "Peasant" team receive a reward (+1). If the "Landlord" wins, then only the "Landlord" receives a reward (+1).

The "Landlord" plays first by putting down a combination of cards. The next player, may pass or put down a higher combination of cards that beat the previous play. There are many legal combinations of cards, outlined in detail in Dou Dizhu's [Wikipedia article](https://en.wikipedia.org/wiki/Dou_dizhu).

Our implementation wraps [RLCard](http://rlcard.org/games.html#dou-dizhu) and you can refer to its documentation for additional details. Please cite their work if you use this game in research.

#### Observation Space

The *Observation Space* is encoded in 6 planes with 5x15 entries each. For each plane, the 5 rows represent 0, 1, 2, 3, or 4 cards of the same rank and the 15 columns represents all possible ranks ("3, 4, 5, 6, 7, 8, 9, 10, J, Q, K, A, 2, Black Joker, and Red Joker"). The first plane, Plane 0, is the current player while Plane 1, Plane 2-4, and Plane 5 correspond to the union of the other two players' hand, the recent three actions, and the union of all played cards, respectively.

#### Action Space

The raw size of the action space of Dou Dizhu is 33,676. Because of this, our implementation of Dou Dizhu abstracts the action space into 309 actions as shown below:

| Action Type      | Number of Actions | Number of Actions after Abstraction | Action ID         |
| ---------------- | :---------------: | :---------------------------------: | :---------------: | 
| Solo             |        15         |        15                           | 0-14              |
| Pair             |        13         |        13                           | 15-27             |
| Trio             |        13         |        13                           | 28-40             |
| Trio with single |        182        |        13                           | 41-53             |
| Trio with pair   |        156        |        13                           | 54-66             |
| Chain of solo    |       36          |        36                           | 67-102            |
| Chain of pair    |       52          |        52                           | 103-154           |
| Chain of trio    |        45         |        45                           | 155-199           |
| Plane with solo  |        24721      |        38                           | 200-237           |
| Plane with pair  |        6552       |        30                           | 238-267           |
| Quad with solo   |       1339        |        13                           | 268-280           |
| Quad with pair   |       1014        |        13                           | 281-293           |
| Bomb             |        13         |        13                           | 294-306           |
| Rocket           |         1         |         1                           | 307               |
| Pass             |         1         |         1                           | 308               |
| Total            |       33676       |        309                          |                   |

For example, you would use action `0` to play a single "3" card or action `30` to play a trio of "5". 

#### Legal Moves

The legal moves available for each agent, found in `env.infos`, are updated after each step.

#### Rewards

| Winner | Loser |
| :----: | ----- |
| +1     | 0     |

### Gin Rummy

| Observations | Actions  | Agents | Manual Control | Action Shape  | Action Values  | Observation Shape | Observation Values | Num States |
|--------------|----------|--------|----------------|---------------|----------------|-------------------|--------------------|------------|
| Graphical    | Discrete | 2      | No             | Discrete(110) | Discrete(110)  | (5, 52)           | [0,1]              | ?          |

`from pettingzoo.classic import gin_rummy`

*gif*

*AEC Diagram*

Gin Rummy is a 2 players card game with a 52 card deck. The objective is to combine 3 or more cards of the same rank or cards in sequence of the same suit. 

Our implementation wraps [RLCard](http://rlcard.org/games.html#gin-rummy) and you can refer to its documentation for additional details. Please cite their work if you use this game in research.

#### Observation Space

The observation space is (5, 52) with the rows representing different planes and columns representing the 52 cards in a deck. The cards are ordered from Ace of spades to King of spades, Ace of hearts to King of hearts, Ace of diamonds to King of diamonds, followed by the Ace of clubs to King of clubs.

The observation and action space descriptions are taken from RLCard.

| Plane |              Feature                                                       |
| :---: | -------------------------------------------------------------------------- |
| 0     | the cards in current player's hand                                         |
| 1     | the top card of the discard pile                                           |
| 2     | the dead cards: cards in discard pile (excluding the top card)             |
| 3     | opponent known cards: cards picked up from discard pile, but not discarded |
| 4     | the unknown cards: cards in stockpile or in opponent hand (but not known)  |

#### Action Space

There are 110 actions in Gin Rummy.

| Action ID     |     Action                 |
| :-----------: | -------------------------- |
| 0             | score_player_0_action      |
| 1             | score_player_1_action      |
| 2             | draw_card_action           |
| 3             | pick_up_discard_action     |
| 4             | declare_dead_hand_action   |
| 5             | gin_action                 |
| 6 - 57        | discard_action             |
| 58 - 109      | knock_action               |

For example, you would use action `2` to draw a card or action `3` to pick up a discarded card. 

#### Legal Moves

The legal moves available for each agent, found in `env.infos`, are updated after each step.

#### Rewards

At the end of the game, a player who gins is awarded 1 point, a player who knocks is awarded 0.2 points, and the losing player recieves a reward equal to  -1 * their deadwood count.

If the hand is declared dead, both players recieve a reward equal to  -1 * their deadwood count.

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

| Observations | Actions  | Agents | Manual Control | Action Shape  | Action Values  | Observation Shape | Observation Values | Num States |
|--------------|----------|--------|----------------|---------------|----------------|-------------------|--------------------|------------|
| Graphical    | Discrete | 2      | No             | Discrete(4)   | Discrete(4)    | (34,)             | [0, Inf]           | ?          |

`from pettingzoo.classic import leduc_holdem`

*gif*

*AEC Diagram*

Leduc Hold'em is a variation of Limit Texas Hold'em with 2 players, 2 rounds and six cards in total (Jack, Queen, and King). At the beginning of the game, each player receives one card and, after betting, one public card is revealed. Another round follow. At the end, the player with the best hand wins and receives a reward (+1) and the loser receives -1. At any time, any player can fold.   

Our implementation wraps [RLCard](http://rlcard.org/games.html#leduc-hold-em) and you can refer to its documentation for additional details. Please cite their work if you use this game in research.

#### Observation Space

As described by [RLCard](https://github.com/datamllab/rlcard/blob/master/docs/games.md#leduc-holdem), the first 3 entries correspond to the player's hand (J, Q, and K) and the next 3 represent the public cards. Indexes 6 to 19 and 20 to 33 encode the number of chips by the current player and the opponent, respectively.

#### Action Space

The action space is encoded as `0` for "Call", `1` for "Raise", `2` for "Fold", and `3` for "Check".

#### Legal Moves

The legal moves available for each agent, found in `env.infos`, are updated after each step.

#### Rewards

| Winner        | Loser         |
| :-----------: | ------------- |
| +raised chips | -raised chips |

### Mahjong

| Observations | Actions  | Agents | Manual Control | Action Shape | Action Values | Observation Shape | Observation Values | Num States |
|--------------|----------|--------|----------------|--------------|---------------|-------------------|--------------------|------------|
| Vector       | Discrete | 4      | No             | Discrete(38) | Discrete(38)  | (6, 34, 4)        | [0, 1]             | ?          |

`from pettingzoo.classic import mahjong`

*gif*

*AEC Diagram*

Mahjong is a tile-based game with 4 players and 136 tiles. The objective is to form 4 sets and a pair with the 14th drawn tile. If no player wins, no player receives a reward.

Our implementation wraps [RLCard](http://rlcard.org/games.html#mahjong) and you can refer to its documentation for additional details. Please cite their work if you use this game in research.

#### Observation Space

The observation space has a (6, 34, 4) shape with the first index representing the encoding plane. Plane 0 represent the current player's hand, Plane 1 represent the played cards on the table, and Planes 2-5 encode the public piles of each player (Plane 2: Player 0, Plane 3: Player 1, Plane 4: Player 2, and Plane 5: Player 3).

#### Action Space

The action space, as described by RLCard, is

| Action ID   |     Action                  |
| ----------- | :-------------------------: |
| 0 ~ 8       | Bamboo-1 ~ Bamboo-9         |
| 9 ~ 17      | Characters-1 ~ Character-9  |
| 18 ~ 26     | Dots-1 ~ Dots-9             |
| 27          | Dragons-green               |
| 28          | Dragons-red                 |
| 29          | Dragons-white               |
| 30          | Winds-east                  |
| 31          | Winds-west                  |
| 32          | Winds-north                 |
| 33          | Winds-south                 |
| 34          | Pong                        |
| 35          | Chow                        |
| 36          | Gong                        |
| 37          | Stand                       |

For example, you would use action `34` to pong or action `37` to stand. 

#### Legal Moves

The legal moves available for each agent, found in `env.infos`, are updated after each step.

#### Rewards

| Winner | Loser |
| :----: | ----- |
| +1     | -1    |

### Rock Paper Scissors

| Observations | Actions | Agents | Manual Control | Action Shape | Action Values | Observation Shape | Observation Values | Num States |
|--------------|----------|---------|----------------|--------------|---------------|-------------------|--------------------|------------|
| ?            | ?       | ?      | ?              | ?            | ?             | ?                 | ?                  | ?          |

`from pettingzoo.classic import rps`

*gif*

*AEC Diagram*

*Blurb*

#### Rewards

| Winner | Loser |
| :----: | ----- |
| +1     | -1    |

If the game ends in a draw, both players will recieve a reward of 0.

### Rock Paper Scissors Lizard Spock

| Observations | Actions | Agents | Manual Control | Action Shape | Action Values | Observation Shape | Observation Values | Num States |
|--------------|----------|---------|----------------|--------------|---------------|-------------------|--------------------|------------|
| ?            | ?       | ?      | ?              | ?            | ?             | ?                 | ?                  | ?          |

`from pettingzoo.classic import rpsls`

*gif*

*AEC Diagram*

*Blurb*

#### Rewards

| Winner | Loser |
| :----: | ----- |
| +1     | -1    |

If the game ends in a draw, both players will recieve a reward of 0.


### Texas Hold'em

| Observations | Actions  | Agents | Manual Control | Action Shape | Action Values | Observation Shape | Observation Values | Num States |
|--------------|----------|--------|----------------|--------------|---------------|-------------------|--------------------|------------|
| Graphical    | Discrete | 2      | No             | Discrete(4)  | Discrete(4)   | (72,)             | [0, 1]           | ?          |

`from pettingzoo.classic import texas_holdem`

*gif*

*AEC Diagram*

Texas Hold'em is a poker game involving 2 players and a regular 52 cards deck. At the beginning, both players get two cards. After betting, three community cards are shown and another round follows. At any time, a player could fold and the game will end. The winner will receive +1 as a reward and the loser will get -1. This is an implementation of the standard limitted version of Texas Hold'm, sometimes referred to as 'Limit Texas Hold'em'.

Our implementation wraps [RLCard](http://rlcard.org/games.html#limit-texas-hold-em) and you can refer to its documentation for additional details. Please cite their work if you use this game in research.

#### Observation Space

The observation space is a vector of 72 boolean integers. The first 52 entries depict the current player's hand plus any community cards as follows

| Index   | Meaning                 |
| ------- | :----------------------:|
| 0~12    | Spade A ~ Spade K       |
| 13~25   | Heart A ~ Heart K       |
| 26~38   | Diamond A ~ Diamond K   |
| 39~51   | Club A ~ Club K         |
| 52~56   | Raise number in round 1 |
| 37~61   | Raise number in round 2 |
| 62~66   | Raise number in round 3 |
| 67~71   | Raise number in round 4 |

#### Action Space

The action space is encoded as `0` for "Call", `1` for "Raise", `2` for "Fold", and `3` for "Check".

#### Legal Moves

The legal moves available for each agent, found in `env.infos`, are updated after each step.

#### Rewards

| Winner          | Loser           |
| :-------------: | --------------- |
| +raised chips/2 | -raised chips/2 |

### Texas Hold'em No Limit

| Observations | Actions  | Agents | Manual Control | Action Shape  | Action Values | Observation Shape | Observation Values | Num States |
|--------------|----------|--------|----------------|---------------|---------------|-------------------|--------------------|------------|
| Graphical    | Discrete | 2      | No             | Discrete(103) | Discrete(103) | (54,)             | [0, 100]           | ?          |

`from pettingzoo.classic import texas_holdem_no_limit`

*gif*

*AEC Diagram*

Texas Hold'em No Limit is a variation of Texas Hold'em where there is no limit on the amount of raise or the number of raises.

Our implementation wraps [RLCard](http://rlcard.org/games.html#no-limit-texas-hold-em) and you can refer to its documentation for additional details. Please cite their work if you use this game in research.

#### Observation Space

The observation space is similar to Texas Hold'em. The first 52 entries represent the current player's hand with any community card.

| Index   | Meaning                     | Values   |
| ------- | :-------------------------- |----------|
| 0~12    | Spade A ~ Spade K           | [0, 1]   |
| 13~25   | Heart A ~ Heart K           | [0, 1]   |
| 26~38   | Diamond A ~ Diamond K       | [0, 1]   |
| 39~51   | Club A ~ Club K             | [0, 1]   |
| 52      | Number of Chips of player 1 | [0, 100] |
| 53      | Number of Chips of player 2 | [0, 100] |

#### Action Space

The action space is encoded as `0` for "Call", `1` for "Fold", `2` for "Checl", and `3` to `102` for "Raise Amount" from 1 to 100.

#### Legal Moves

The legal moves available for each agent, found in `env.infos`, are updated after each step.

#### Rewards

| Winner          | Loser           |
| :-------------: | --------------- |
| +raised chips/2 | -raised chips/2 |

### Tic Tac Toe

| Observations | Actions | Agents | Manual Control | Action Shape | Action Values | Observation Shape | Observation Values | Num States |
|--------------|----------|---------|----------------|--------------|---------------|-------------------|--------------------|------------|
| ?            | Discrete | 2       | yes            | (1)          | [0, 9]        | (3, 3)            | [0,1,2]            | ?          |

`from pettingzoo.classic import tictactoe`

*gif*

*AEC Diagram*

Tic-tac-toe is a simple turn based strategy game where 2 players, X and O, take turns marking spaces on a 3 x 3 grid. The first player to place 3 of their marks in a horizontal, vertical, or diagonal row is the winner.

#### Observation Space

#### Action Space

#### Rewards

| Winner | Loser |
| :----: | ----- |
| +1     | -1    |

If the game ends in a draw, both players will recieve a reward of 0.

### Uno

| Observations | Actions  | Agents | Manual Control | Action Shape | Action Values | Observation Shape | Observation Values | Num States |
|--------------|----------|--------|----------------|--------------|---------------|-------------------|--------------------|------------|
| Vector       | Discrete | 2      | No             | Discrete(61) | Discrete(61)  | (7, 4, 15)        | [0, 1]             | ?          |

`from pettingzoo.classic import uno`

*gif*

*AEC Diagram*

Uno is shedding game involving 2 players. At the beginning, each player receives 7 cards and the winner is determined as the first player with no cards left. In order to get rid of a card, a player must match either the color and number of the card on top of the discard pile. If the player does not have a card to discard, then it will take a card from the Draw pile. The deck of cards include 4 colors (blue, green, yellow, and red), 10 numbers (0 to 9), and special cards (Wild Draw Four, Skip, Reverse).

Our implementation wraps [RLCard](http://rlcard.org/games.html#uno) and you can refer to its documentation for additional details. Please cite their work if you use this game in research.

#### Observation Space

The observation space has a shape of (7, 4, 15). The first index represent the plane, the second index the color, and the last index the card number (including any special card).

| Plane | Feature                                                   |
| ----- | :-------------------------------------------------------- |
| 0     | Player's Hand with 0 cards of the same color and number   |
| 1     | Player's Hand with 1 card of the same color and number    |
| 2     | Player's Hand with 2 cards of the same color and number   |
| 3     | target card (top of the Discard pile)                     |
| 4     | Opponent's Hand with 0 cards of the same color and number |
| 5     | Opponent's Hand with 1 cards of the same color and number |
| 6     | Opponent's Hand with 2 cards of the same color and number |

#### Action Space

The action space is as described by RLCards.

| Action ID |                   Action                   |
| --------- | :----------------------------------------: |
| 0~9       |        Red number cards from 0 to 9        |
| 10~12     |  Red action cards: skip, reverse, draw 2   |
| 13        |               Red wild card                |
| 14        |          Red wild and draw 4 card          |
| 15~24     |       green number cards from 0 to 9       |
| 25~27     | green action cards: skip, reverse, draw 2  |
| 28        |              green wild card               |
| 29        |         green wild and draw 4 card         |
| 30~39     |       blue number cards from 0 to 9        |
| 40~42     |  blue action cards: skip, reverse, draw 2  |
| 43        |               blue wild card               |
| 44        |         blue wild and draw 4 card          |
| 45~54     |      yellow number cards from 0 to 9       |
| 55~57     | yellow action cards: skip, reverse, draw 2 |
| 58        |              yellow wild card              |
| 59        |        yellow wild and draw 4 card         |
| 60        |                    draw                    |

For example, you would use action `6` to put down a red "6" card or action `60` to draw a card. 

#### Legal Moves

The legal moves available for each agent, found in `env.infos`, are updated after each step.

#### Rewards

| Winner | Loser |
| :----: | ----- |
| +1     | -1    |
