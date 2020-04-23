## Classic Environments

| Environment                      | Actions  | Agents | Manual Control | Action Shape  | Action Values  | Observation Shape | Observation Values | Num States    |
|----------------------------------|----------|--------|----------------|---------------|----------------|-------------------|--------------------|---------------|
| Backgammon                       | ?        | ?      | ?              | ?             | ?              | ?                 | ?                  | ?             |
| Checkers                         | ?        | ?      | ?              | ?             | ?              | ?                 | ?                  | ?             |
| Chess                            | Discrete | 2      | No             | Discrete(4672)| Discrete(4672) | (8,8,20)          | [0,1]              | ?             |
| Connect Four                     | ?        | ?      | ?              | ?             | ?              | ?                 | ?                  | ?             |
| Dou Dizhu                        | Discrete | 3      | No             | Discrete(309) | Discrete(309)  | (6, 5, 15)        | [0,1]              | 10^53 - 10^83 |
| Gin Rummy                        | Discrete | 2      | No             | Discrete(110) | Discrete(110)  | (5, 52)           | [0,1]              | 10^52         |
| Go                               | ?        | ?      | ?              | ?             | ?              | ?                 | ?                  | ?             |
| Leduc Hold'em                    | Discrete | 2      | No             | Discrete(4)   | Discrete(4)    | (36,)             | [0, 1]             | 10^2          |
| Mahjong                          | Discrete | 4      | No             | Discrete(38)  | Discrete(38)   | (6, 34, 4)        | [0, 1]             | 10^121        |
| Rock Paper Scissors              | ?        | ?      | ?              | ?             | ?              | ?                 | ?                  | ?             |
| Rock Paper Scissors Lizard Spock | ?        | ?      | ?              | ?             | ?              | ?                 | ?                  | ?             |
| Texas Hold'em                    | Discrete | 2      | No             | Discrete(4)   | Discrete(4)    | (72,)             | [0, 1]             | 10^14         |
| Texas Hold'em No Limit           | Discrete | 2      | No             | Discrete(103) | Discrete(103)  | (54,)             | [0, 100]           | 10^162        |
| Tic Tac Toe                      | ?        | ?      | ?              | ?             | ?              | ?                 | ?                  | ?             |
| Uno                              | Discrete | 2      | No             | Discrete(61)  | Discrete(61)   | (7, 4, 15)        | [0, 1]             | 10^163        |

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

### Backgammon

| Observations | Actions | Agents | Manual Control | Action Shape | Action Values | Observation Shape | Observation Values | Num States |
|--------------|----------|---------|----------------|--------------|---------------|-------------------|--------------------|------------|
| ?            | ?       | ?      | ?              | ?            | ?             | ?                 | ?                  | ?          |

`from pettingzoo.classic import backgammon_v0`

`agents= `

*gif*

*AEC Diagram*

*Blurb*


### Checkers

| Actions | Agents | Manual Control | Action Shape | Action Values | Observation Shape | Observation Values | Num States |
|----------|---------|----------------|--------------|---------------|-------------------|--------------------|------------|
| ?            | ?       | ?      | ?              | ?            | ?             | ?                 | ?                  | ?          |

`from pettingzoo.classic import checkers_v0`

`agents= `

*gif*

*AEC Diagram*

*Blurb*

#### Observation Space

#### Action Space

#### Rewards

| Winner | Loser |
| :----: | :---: |
| +1     | -1    |

### Chess

| Actions  | Agents | Manual Control | Action Shape                           | Action Values  | Observation Shape | Observation Values | Num States |
|----------|--------|----------------|----------------------------------------|----------------|-------------------|--------------------|------------|
| Graphical    | Discrete | 2      | No             | Discrete(4672) | Discrete(4672) | (8,8,20)          | [0,1]              | ?          |

`pettingzoo.classic.chess_v0`

`agents= ['player_1', 'player_2']`

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
| :----: | :---: |
| +1     | -1    |


#### Legal Moves

The legal moves available for each agent, found in `env.infos[agent]['legal_moves']`, are updated after each step. Taking an illegal move ends the game with a reward of -1 for the illegally moving agent and a reward of 0 for all other agents


### Dou Dizhu

| Actions  | Agents | Manual Control | Action Shape  | Action Values  | Observation Shape | Observation Values | Num States    |
|----------|--------|----------------|---------------|----------------|-------------------|--------------------|---------------|
| Vector       | Discrete | 3      | No             | Discrete(309) | Discrete(309)  | (6, 5, 15)        | [0,1]              | 10^53 - 10^83 |

`from pettingzoo.classic import dou_dizhu_v0`

`agents= ['landlord_0', 'peasant_0', 'peasant_1']`

*gif*

*AEC Diagram*

Dou Dizhu, or *Fighting the Landlord*, is a shedding game involving 3 players and a deck of cards plus 2 jokers with suits being irrelevant. Heuristically, one player is designated the "Landlord" and the others become the "Peasants". The objective of the game is to be the first one to have no cards left. If the first person to have no cards left is part of the "Peasant" team, then all members of the "Peasant" team receive a reward (+1). If the "Landlord" wins, then only the "Landlord" receives a reward (+1).

The "Landlord" plays first by putting down a combination of cards. The next player, may pass or put down a higher combination of cards that beat the previous play. There are many legal combinations of cards, outlined in detail in Dou Dizhu's [Wikipedia article](https://en.wikipedia.org/wiki/Dou_dizhu).

Our implementation wraps [RLCard](http://rlcard.org/games.html#dou-dizhu) and you can refer to its documentation for additional details. Please cite their work if you use this game in research.

#### Observation Space

The *Observation Space* is encoded in 6 planes with 5x15 entries each. For each plane, the 5 rows represent 0, 1, 2, 3, or 4 cards of the same rank and the 15 columns represents all possible ranks ("3, 4, 5, 6, 7, 8, 9, 10, J, Q, K, A, 2, Black Joker, and Red Joker"). The first plane, Plane 0, is the current player while Plane 1, Plane 2-4, and Plane 5 correspond to the union of the other two players' hand, the recent three actions, and the union of all played cards, respectively.

| Plane | Description                      |
|:-----:|----------------------------------|
|   0   | Current Player's hand            |
|   1   | Union of the other players' hand |
| 2 - 4 | Recent three actions             |
|   5   | Union of all played card         |

##### Encoding per Plane

| Plane Row Index |          Description          |
|:---------------:| ----------------------------- |
|        0        | 0 matching cards of same rank |
|        1        | 1 matching cards of same rank |
|        2        | 2 matching cards of same rank |
|        3        | 3 matching cards of same rank |
|        4        | 4 matching cards of same rank |

| Plane Column Index | Description |
|:------------------:|-------------|
|          0         | 3           |
|          1         | 4           |
|         ...        | ...         |
|          7         | 10          |
|          8         | Jack        |
|          9         | Queen       |
|         10         | King        |
|         11         | Ace         |
|         12         | 2           |
|         13         | Black Joker |
|         14         | Red Joker   |

#### Action Space

The raw size of the action space of Dou Dizhu is 33,676. Because of this, our implementation of Dou Dizhu abstracts the action space into 309 actions as shown below. The core idea is to abstract actions by only focusing on the major combination and ignoring the kicker (e.g. a trio with single "4445" would be "444&ast;"). As a reminder, suits are irrelevant in Dou Dizhu.

| Action Type      | Description                                                                         | Number of Actions | Number of Actions after Abstraction | Action ID | Example                                                                                                                                                                                                                                                          |
|------------------|-------------------------------------------------------------------------------------|-------------------|-------------------------------------|-----------|------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| Solo             | Any single card                                                                     | 15                | 15                                  | 0-14      | `0`: 3, `1`: 4, ..., `12`: 2, `13`: Black Joker, `14`: Red Joker                                                                                                                                                                                                 |
| Pair             | Two matching cards of equal rank                                                    | 13                | 13                                  | 15-27     | `15`: 33, `16`: 44, ..., `25`: KK, `26`: AA, `27`: 22                                                                                                                                                                                                            |
| Trio             | Three matching cards of equal rank                                                  | 13                | 13                                  | 28-40     | `28`: 333, `29`: 444, ..., `38`: KKK, `39`: AAA, `40`: 222                                                                                                                                                                                                       |
| Trio with single | Three matching cards of equal rank + single card of next higher rank (e.g. 3334)    | 182               | 13                                  | 41-53     | `41`: 333&ast;, `42`: 444&ast;, ..., `51`: KKK&ast;, `52`: AAA&ast;, `53`: 222&ast;                                                                                                                                                                              |
| Trio with pair   | Three matching cards of equal rank + pair of cards of next higher rank (e.g. 33344) | 156               | 13                                  | 54-66     | `54`: 333&ast;&ast;, `55`: 444&ast;&ast;, ..., `64`: KKK&ast;&ast;, `65`: AAA&ast;&ast;, `66`: 222&ast;&ast;                                                                                                                                                     |
| Chain of solo    | At least five consecutive solo cards                                                | 36                | 36                                  | 67-102    | `67`: 34567, `68`: 45678, ..., `100`: 3456789TJQK, `101`: 456789TJQKA, `102`: 3456789TJQKA                                                                                                                                                                       |
| Chain of pair    | At least three consecutive pairs                                                    | 52                | 52                                  | 103-154   | `103`: 334455, `104`: 445566, ..., `152`: 33445566778899TTJJQQ, `153`: 445566778899TTJJQQKK, `154`: 5566778899TTJJQQKKAA                                                                                                                                         |
| Chain of trio    | At least two consecutive trios                                                      | 45                | 45                                  | 155-199   | `155`: 333444, `156`: 444555, ..., `197`: 777888999TTTJJJQQQ, `198`: 888999TTTJJJQQQKKK, `199`: 999TTTJJJQQQKKKAAA                                                                                                                                               |
| Plane with solo  | Two consecutive trios + 2 consecutive solo cards (e.g. 33344456)                    | 24721             | 38                                  | 200-237   | `200`: 333444&ast;&ast;, `201`: 444555&ast;&ast;, ..., `235`: 888999TTTJJJQQQ&ast;&ast;&ast;&ast;&ast;, `236`: 999TTTJJJQQQKKK&ast;&ast;&ast;&ast;&ast;, `237`: TTTJJJQQQKKKAAA&ast;&ast;&ast;&ast;&ast;                                                         |
| Plane with pair  | Two consecutive trios + 2 consecutive pairs (e.g. 3334445566)                       | 6552              | 30                                  | 238-267   | `238`: 333444&ast;&ast;&ast;&ast;, `239`: 444555&ast;&ast;&ast;&ast;, ..., `265`: 999TTTJJJQQQ&ast;&ast;&ast;&ast;&ast;&ast;&ast;&ast;, `266`: TTTJJJQQQKKK&ast;&ast;&ast;&ast;&ast;&ast;&ast;&ast;, `267`: JJJQQQKKKAAA&ast;&ast;&ast;&ast;&ast;&ast;&ast;&ast; |
| Quad with solo   | Four matching cards of equal rank + 2 consecutive solo cards (e.g 333345)           | 1339              | 13                                  | 268-280   | `268`: 3333&ast;&ast;, `269`: 4444&ast;&ast;, ..., `278`: KKKK&ast;&ast;, `279`: AAAA&ast;&ast;, `280`: 2222&ast;&ast;                                                                                                                                           |
| Quad with pair   | Four matching cards of equal rank + 2 consecutive pair (e.g 33334455)               | 1014              | 13                                  | 281-293   | `281`: 3333&ast;&ast;&ast;&ast;, `282`: 4444&ast;&ast;&ast;&ast;, ..., `291`: KKKK&ast;&ast;&ast;&ast;, `292`: AAAA&ast;&ast;&ast;&ast;, `293`: 2222&ast;&ast;&ast;&ast;                                                                                         |
| Bomb             | Four matching cards of equal rank                                                   | 13                | 13                                  | 294-306   | `294`: 3333, `295`: 4444, ..., `304`: KKKK, `305`: AAAA, `306`: 2222                                                                                                                                                                                             |
| Rocket           | Black Joker + Red Joker                                                             | 1                 | 1                                   | 307       | `307`: Black Joker (B) + Red Joker (R)                                                                                                                                                                                                                           |
| Pass             | Pass                                                                                | 1                 | 1                                   | 308       | `308`: Pass                                                                                                                                                                                                                                                      |
| Total            |                                                                                     | 33676             | 309                                 |           |                                                                                                                                                                                                                                                                  |                                                                                                                                                                                                                            |

For example, you would use action `0` to play a single "3" card or action `30` to play a trio of "5". 

#### Rewards

We modified the reward structure compared to RLCard. Instead of rewarding `0` to the losing player, we assigned a `-1` reward to the losing agent.

| Winner | Loser |
| :----: | :---: |
| +1     |   -1  |

#### Legal Moves

The legal moves available for each agent, found in `env.infos[agent]['legal_moves']`, are updated after each step. Taking an illegal move ends the game with a reward of -1 for the illegally moving agent and a reward of 0 for all other agents


### Gin Rummy

| Actions  | Agents | Manual Control | Action Shape  | Action Values  | Observation Shape | Observation Values | Num States |
|----------|--------|----------------|---------------|----------------|-------------------|--------------------|------------|
| Graphical    | Discrete | 2      | No             | Discrete(110) | Discrete(110)  | (5, 52)           | [0,1]              | 10^52      |

`from pettingzoo.classic import gin_rummy_v0`

`agents= ['player_0', 'player_1']`

*gif*

*AEC Diagram*

Gin Rummy is a 2 players card game with a 52 card deck. The objective is to combine 3 or more cards of the same rank or cards in sequence of the same suit. 

Our implementation wraps [RLCard](http://rlcard.org/games.html#gin-rummy) and you can refer to its documentation for additional details. Please cite their work if you use this game in research.

#### Arguments

Gin Rummy takes two optional arguments that define the reward received by a player who knocks or goes gin. The default values for the knock reward and gin reward are 0.5 and 1.0, respectively.

`gin_rummy_v0.env(knock_reward = 0.5, gin_reward = 1.0)`

`gin_rummy_v0.env() # with default values`

#### Observation Space

The observation space is (5, 52) with the rows representing different planes and columns representing the 52 cards in a deck. The cards are ordered from Ace of spades to King of spades, Ace of hearts to King of hearts, Ace of diamonds to King of diamonds, followed by the Ace of clubs to King of clubs.

| Row Index | Description                                    |
|:---------:|------------------------------------------------|
|     0     | Current player's hand                          |
|     1     | Top card of the discard pile                   |
|     2     | Cards in discard pile (excluding the top card) |
|     3     | Opponent's known cards                         |
|     4     | Unknown cards                                  |

| Column Index | Description                                       |
|:------------:|---------------------------------------------------|
|    0 - 12    | Spades<br>_`0`: Ace, `1`: 2, ..., `12`: King_     |
|    13 - 25   | Hearts<br>_`13`: Ace, `14`: 2, ..., `25`: King_   |
|    26 - 38   | Diamonds<br>_`26`: Ace, `27`: 2, ..., `38`: King_ |
|    39 - 51   | Clubs<br>_`39`: Ace, `40`: 2, ..., `51`: King_    |

#### Action Space

There are 110 actions in Gin Rummy.

| Action ID | Action                                                                                                                                                                                 |
|:---------:|----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
|     0     | Score Player 0<br>_Used after knock, gin, or dead hand to compute the player's hand._                                                                                                  |
|     1     | Score Player 1<br>_Used after knock, gin, or dead hand to compute the player's hand._                                                                                                  |
|     2     | Draw a card                                                                                                                                                                            |
|     3     | Pick top card from Discard pile                                                                                                                                                        |
|     4     | Declare dead hand                                                                                                                                                                      |
|     5     | Gin                                                                                                                                                                                    |
|   6 - 57  | Discard a card<br>_`6`: A-Spades, `7`: 2-Spades, ..., `18`: K-Spades<br>`19`: A-Hearts ... `31`: K-Hearts<br>`32`: A-Diamonds ... `44`: K-Diamonds<br>`45`: A-Clubs ... `57`: K-Clubs_ |
|  58 - 109 | Knock<br>_`58`: A-Spades, `59`: 2-Spades, ..., `70`: K-Spades<br>`71`: A-Hearts ... `83`: K-Hearts<br>`84`: A-Diamonds ... `96`: K-Diamonds<br>`97`: A-Clubs ... `109`: K-Clubs_       |

For example, you would use action `2` to draw a card or action `3` to pick up a discarded card. 

#### Rewards

At the end of the game, a player who gins is awarded 1 point, a player who knocks is awarded 0.5 points, and the losing player receives a reward equal to the negative of their deadwood count.

If the hand is declared dead, both players get a reward equal to negative of their deadwood count.

| End Action                                | Winner | Loser               |
|-------------------------------------------|:------:|---------------------|
| Dead Hand<br>_Both players are penalized_ |   --   | -deadwood_count/100 |
| Knock<br>_Knocking player: Default +0.5_  |   --   | -deadwood_count/100 |
| Gin<br>_Going Gin Player: Default +1_     |   --   | -deadwood_count/100 |

Note that the defaults are slightly different from those in RLcard- their default reward for knocking is 0.2.

Penalties of deadwood_count/100 ensure that the reward never goes below -1.

#### Legal Moves

The legal moves available for each agent, found in `env.infos[agent]['legal_moves']`, are updated after each step. Taking an illegal move ends the game with a reward of -1 for the illegally moving agent and a reward of 0 for all other agents


### Go

| Actions | Agents | Manual Control | Action Shape | Action Values | Observation Shape | Observation Values | Num States |
|----------|---------|----------------|--------------|---------------|-------------------|--------------------|------------|
| ?            | ?       | ?      | ?              | ?            | ?             | ?                 | ?                  | ?          |

`from pettingzoo.classic import go_v0`

`agents= `

*gif*

*AEC Diagram*

*Blurb*

*Env arguments*

*About env arguments*

### Leduc Hold'em

| Observations | Actions  | Agents | Manual Control | Action Shape  | Action Values  | Observation Shape | Observation Values | Num States |
|--------------|----------|--------|----------------|---------------|----------------|-------------------|--------------------|------------|
| Graphical    | Discrete | 2      | No             | Discrete(4)   | Discrete(4)    | (36,)             | [0, 1]             | 10^2       |

`from pettingzoo.classic import leduc_holdem_v0`

`agents= ['player_0', 'player_1']`

*gif*

*AEC Diagram*

Leduc Hold'em is a variation of Limit Texas Hold'em with 2 players, 2 rounds and six cards in total (Jack, Queen, and King). At the beginning of the game, each player receives one card and, after betting, one public card is revealed. Another round follow. At the end, the player with the best hand wins and receives a reward (+1) and the loser receives -1. At any time, any player can fold.   

Our implementation wraps [RLCard](http://rlcard.org/games.html#leduc-hold-em) and you can refer to its documentation for additional details. Please cite their work if you use this game in research.

#### Observation Space

As described by [RLCard](https://github.com/datamllab/rlcard/blob/master/docs/games.md#leduc-holdem), the first 3 entries correspond to the player's hand (J, Q, and K) and the next 3 represent the public cards. Indexes 6 to 19 and 20 to 33 encode the number of chips by the current player and the opponent, respectively.

|  Index  | Description                                                                  |
|:-------:|------------------------------------------------------------------------------|
|  0 - 2  | Current Player's Hand<br>_`0`: J, `1`: Q, `2`: K_                            |
|  3 - 5  | Community Cards<br>_`3`: J, `4`: Q, `5`: K_                                  |
|  6 - 20 | Current Player's Chips<br>_`6`: 0 chips, `7`: 1 chip, ..., `20`: 14 chips_   |
| 21 - 35 | Opponent's Chips<br>_`21`: 0 chips, `22`: 1 chip, ..., `35`: 14 chips_       |

#### Action Space

| Action ID | Action |
|:---------:|--------|
|     0     | Call   |
|     1     | Raise  |
|     2     | Fold   |
|     3     | Check  |

#### Rewards

| Winner          | Loser           |
| :-------------: | :-------------: |
| +raised chips/2 | -raised chips/2 |

#### Legal Moves

The legal moves available for each agent, found in `env.infos[agent]['legal_moves']`, are updated after each step. Taking an illegal move ends the game with a reward of -1 for the illegally moving agent and a reward of 0 for all other agents


### Mahjong

| Actions  | Agents | Manual Control | Action Shape | Action Values | Observation Shape | Observation Values | Num States |
|----------|--------|----------------|--------------|---------------|-------------------|--------------------|------------|
| Vector       | Discrete | 4      | No             | Discrete(38) | Discrete(38)  | (6, 34, 4)        | [0, 1]             | 10^121     |

`from pettingzoo.classic import mahjong_v0`

`agents= ['player_0', 'player_1', 'player_2', 'player_3']`

*gif*

*AEC Diagram*

Mahjong is a tile-based game with 4 players and 136 tiles, which includes 4 identical sets of 34 unique tiles. The objective is to form 4 sets and a pair with the 14th drawn tile. If no player wins, no player receives a reward.

Our implementation wraps [RLCard](http://rlcard.org/games.html#mahjong) and you can refer to its documentation for additional details. Please cite their work if you use this game in research.

#### Observation Space

The observation space has a (6, 34, 4) shape with the first index representing the encoding plane. Plane 0 represent the current player's hand, Plane 1 represent the played cards on the table, and Planes 2-5 encode the public piles of each player (Plane 2: Player 0, Plane 3: Player 1, Plane 4: Player 2, and Plane 5: Player 3).

| Plane | Description               |
|:-----:|---------------------------|
|   0   | Current Player's hand     |
|   1   | Played tiles on the table |
|   2   | Public piles of player_0  |
|   3   | Public piles of player_1  |
|   4   | Public piles of player_2  |
|   5   | Public piles of player_3  |

##### Encoding per Plane

| Plane Row Index | Description                                   |
|:---------------:|-----------------------------------------------|
|      0 - 8      | Bamboo<br>_`0`: 1, `1`: 2, ..., `8`: 9_       |
|      9 - 17     | Characters<br>_`9`: 1, `10`: 2, ..., `17`: 9_ |
|     18 - 26     | Dots<br>_`18`: 1, `19`: 2, ..., `26`: 9_      |
|        27       | Dragons Green                                 |
|        28       | Dragons Red                                   |
|        29       | Dragons White                                 |
|        30       | Winds East                                    |
|        31       | Winds West                                    |
|        32       | Winds North                                   |
|        33       | Winds South                                   |

| Plane Column Index | Description |
|:------------------:|-------------|
|          0         | Tile Set 1  |
|          1         | Tile Set 2  |
|          2         | Tile Set 3  |
|          3         | Tile Set 4  |

#### Action Space

The action space, as described by RLCard, is

| Action ID   | Action                                         |
| :---------: | ---------------------------------------------- |
| 0 - 8       | Bamboo<br>_`0`: 1, `1`: 2, ..., `8`: 9_        |
| 9 - 17      | Characters<br>_`9`: 1, `10`: 2, ..., `17`: 9_  |
| 18 - 26     | Dots<br>_`18`: 1, `19`: 2, ..., `26`: 9_       |
| 27          | Dragons Green                                  |
| 28          | Dragons Red                                    |
| 29          | Dragons White                                  |
| 30          | Winds East                                     |
| 31          | Winds West                                     |
| 32          | Winds North                                    |
| 33          | Winds South                                    |
| 34          | Pong                                           |
| 35          | Chow                                           |
| 36          | Gong                                           |
| 37          | Stand                                          |

For example, you would use action `34` to pong or action `37` to stand. 

#### Rewards

| Winner | Loser |
| :----: | :---: |
| +1     | -1    |

#### Legal Moves

The legal moves available for each agent, found in `env.infos[agent]['legal_moves']`, are updated after each step. Taking an illegal move ends the game with a reward of -1 for the illegally moving agent and a reward of 0 for all other agents


### Rock Paper Scissors

| Actions | Agents | Manual Control | Action Shape | Action Values | Observation Shape | Observation Values | Num States |
|----------|---------|----------------|--------------|---------------|-------------------|--------------------|------------|
| ?            | ?       | ?      | ?              | ?            | ?             | ?                 | ?                  | ?          |

`from pettingzoo.classic import rps_v0`

`agents= `

*gif*

*AEC Diagram*

*Blurb*

#### Rewards

| Winner | Loser |
| :----: | :---: |
| +1     | -1    |

If the game ends in a draw, both players will receive a reward of 0.

### Rock Paper Scissors Lizard Spock

| Actions | Agents | Manual Control | Action Shape | Action Values | Observation Shape | Observation Values | Num States |
|----------|---------|----------------|--------------|---------------|-------------------|--------------------|------------|
| ?            | ?       | ?      | ?              | ?            | ?             | ?                 | ?                  | ?          |

`from pettingzoo.classic import rpsls_v0`

`agents= `

*gif*

*AEC Diagram*

*Blurb*

#### Rewards

| Winner | Loser |
| :----: | :---: |
| +1     | -1    |

If the game ends in a draw, both players will receive a reward of 0.

### Texas Hold'em
| Actions  | Agents | Manual Control | Action Shape | Action Values | Observation Shape | Observation Values | Num States |
|----------|--------|----------------|--------------|---------------|-------------------|--------------------|------------|
| Graphical    | Discrete | 2      | No             | Discrete(4)  | Discrete(4)   | (72,)             | [0, 1]             | 10^14      |

`from pettingzoo.classic import texas_holdem_v0`

`agents= ['player_0', 'player_1']`

*gif*

*AEC Diagram*

Texas Hold'em is a poker game involving 2 players and a regular 52 cards deck. At the beginning, both players get two cards. After betting, three community cards are shown and another round follows. At any time, a player could fold and the game will end. The winner will receive +1 as a reward and the loser will get -1. This is an implementation of the standard limitted version of Texas Hold'm, sometimes referred to as 'Limit Texas Hold'em'.

Our implementation wraps [RLCard](http://rlcard.org/games.html#limit-texas-hold-em) and you can refer to its documentation for additional details. Please cite their work if you use this game in research.

#### Observation Space

The observation space is a vector of 72 boolean integers. The first 52 entries depict the current player's hand plus any community cards as follows

|  Index  | Description                                                 |
|:-------:|-------------------------------------------------------------|
|  0 - 12 | Spades<br>_`0`: A, `1`: 2, ..., `12`: K_                    |
| 13 - 25 | Hearts<br>_`13`: A, `14`: 2, ..., `25`: K_                  |
| 26 - 38 | Diamonds<br>_`26`: A, `27`: 2, ..., `38`: K_                |
| 39 - 51 | Clubs<br>_`39`: A, `40`: 2, ..., `51`: K_                   |
| 52 - 56 | Chips raised in Round 1<br>_`52`: 0, `53`: 1, ..., `56`: 4_ |
| 57 - 61 | Chips raised in Round 2<br>_`57`: 0, `58`: 1, ..., `61`: 4_ |
| 62 - 66 | Chips raised in Round 3<br>_`62`: 0, `63`: 1, ..., `66`: 4_ |
| 67 - 71 | Chips raised in Round 4<br>_`67`: 0, `68`: 1, ..., `71`: 4_ |

#### Action Space

| Action ID | Action |
|:---------:|--------|
|     0     | Call   |
|     1     | Raise  |
|     2     | Fold   |
|     3     | Check  |

#### Rewards

| Winner          | Loser           |
| :-------------: | :-------------: |
| +raised chips/2 | -raised chips/2 |

#### Legal Moves

The legal moves available for each agent, found in `env.infos[agent]['legal_moves']`, are updated after each step. Taking an illegal move ends the game with a reward of -1 for the illegally moving agent and a reward of 0 for all other agents


### Texas Hold'em No Limit

| Actions  | Agents | Manual Control | Action Shape  | Action Values | Observation Shape | Observation Values | Num States |
|----------|--------|----------------|---------------|---------------|-------------------|--------------------|------------|
| Graphical    | Discrete | 2      | No             | Discrete(103) | Discrete(103) | (54,)             | [0, 100]           | 10^162     |

`from pettingzoo.classic import texas_holdem_no_limit_v0`

`agents= ['player_0', 'player_1']`

*gif*

*AEC Diagram*

Texas Hold'em No Limit is a variation of Texas Hold'em where there is no limit on the amount of raise or the number of raises.

Our implementation wraps [RLCard](http://rlcard.org/games.html#no-limit-texas-hold-em) and you can refer to its documentation for additional details. Please cite their work if you use this game in research.

#### Observation Space

The observation space is similar to Texas Hold'em. The first 52 entries represent the current player's hand with any community card.

|  Index  | Description                                  |  Values  |
|:-------:|----------------------------------------------|:--------:|
|  0 - 12 | Spades<br>_`0`: A, `1`: 2, ..., `12`: K_     |  [0, 1]  |
| 13 - 25 | Hearts<br>_`13`: A, `14`: 2, ..., `25`: K_   |  [0, 1]  |
| 26 - 38 | Diamonds<br>_`26`: A, `27`: 2, ..., `38`: K_ |  [0, 1]  |
| 39 - 51 | Clubs<br>_`39`: A, `40`: 2, ..., `51`: K_    |  [0, 1]  |
|    52   | Number of Chips of player_0                  | [0, 100] |
|    53   | Number of Chips of player_1                  | [0, 100] |

#### Action Space

| Action ID | Action                                                      |
|:---------:|-------------------------------------------------------------|
|     0     | Call                                                        |
|     1     | Raise                                                       |
|     2     | Check                                                       |
|  3 - 102  | Raise<br>_`3`: 1 chip, `4`: 2 chips, ..., `102`: 100 chips_ |

#### Rewards

| Winner          | Loser           |
| :-------------: | :-------------: |
| +raised chips/2 | -raised chips/2 |

#### Legal Moves

The legal moves available for each agent, found in `env.infos[agent]['legal_moves']`, are updated after each step. Taking an illegal move ends the game with a reward of -1 for the illegally moving agent and a reward of 0 for all other agents


### Tic Tac Toe
| Actions | Agents | Manual Control | Action Shape | Action Values | Observation Shape | Observation Values | Num States |
|----------|---------|----------------|--------------|---------------|-------------------|--------------------|------------|
| ?            | Discrete | 2       | yes            | (1)          | [0, 9]        | (3, 3)            | [0,1,2]            | ?          |

`from pettingzoo.classic import tictactoe_v0`

`agents= `

*gif*

*AEC Diagram*

Tic-tac-toe is a simple turn based strategy game where 2 players, X and O, take turns marking spaces on a 3 x 3 grid. The first player to place 3 of their marks in a horizontal, vertical, or diagonal row is the winner.

#### Observation Space

#### Action Space

#### Rewards

| Winner | Loser |
| :----: | :---: |
| +1     | -1    |

If the game ends in a draw, both players will receive a reward of 0.

### Uno

| Actions  | Agents | Manual Control | Action Shape | Action Values | Observation Shape | Observation Values | Num States |
|----------|--------|----------------|--------------|---------------|-------------------|--------------------|------------|
| Vector       | Discrete | 2      | No             | Discrete(61) | Discrete(61)  | (7, 4, 15)        | [0, 1]             | 10^163     |

`from pettingzoo.classic import uno_v0`

`agents= ['player_0', 'player_1']`

*gif*

*AEC Diagram*

Uno is shedding game involving 2 players. At the beginning, each player receives 7 cards and the winner is determined as the first player with no cards left. In order to get rid of a card, a player must match either the color and number of the card on top of the discard pile. If the player does not have a card to discard, then it will take a card from the Draw pile. The deck of cards include 4 colors (blue, green, yellow, and red), 10 numbers (0 to 9), and special cards (Wild Draw Four, Skip, Reverse).

Our implementation wraps [RLCard](http://rlcard.org/games.html#uno) and you can refer to its documentation for additional details. Please cite their work if you use this game in research.

#### Observation Space

The observation space has a shape of (7, 4, 15). The first index represent the plane, the second index the color, and the last index the card number (including any special card).

| Plane | Feature                                                   |
| :---: | --------------------------------------------------------- |
| 0     | Player's Hand with 0 cards of the same color and number   |
| 1     | Player's Hand with 1 card of the same color and number    |
| 2     | Player's Hand with 2 cards of the same color and number   |
| 3     | Target card (top of the Discard pile)                     |
| 4     | Opponent's Hand with 0 cards of the same color and number |
| 5     | Opponent's Hand with 1 cards of the same color and number |
| 6     | Opponent's Hand with 2 cards of the same color and number |

##### Encoding per Plane

| Plane Row Index | Description |
|:---------------:|-------------|
|        0        | Red         |
|        1        | Green       |
|        2        | Blue        |
|        3        | Yellow      |

| Plane Column Index | Description    |
|:------------------:|----------------|
|        0           | 0              |
|        1           | 1              |
|        2           | 2              |
|       ...          | ...            |
|        9           | 9              |
|        10          | Wild           |
|        11          | Wild Draw Four |
|        12          | Skip           |
|        13          | Draw Two       |
|        14          | Reverse        |

#### Action Space

The action space is as described by RLCards.

| Action ID |                                     Action                                     |
|:---------:| ------------------------------------------------------------------------------ |
|  0 - 9    | Red number cards<br>_`0`: 0-Red, `1`: 1-Red, ..., `9`: 9-Red_                  |
| 10 - 12   | Red action cards<br>_`10`: Skip, `11`: Reverse, `12`: Draw 2_                  |
|     13    | Red "Wild" card                                                                |
|     14    | Red "Wild and Draw 4" card                                                     |
| 15 - 24   | Green number cards<br>_`15`: 0-Green, `16`: 1-Green, ..., `24`: 9-Green_       |
| 25 - 27   | Green action cards<br>_`25`: Skip, `26`: Reverse, `27`: Draw 2_                |
|     28    | Green "Wild" card                                                              |
|     29    | Green "Wild and draw 4" card                                                   |
| 30 - 39   | Blue number cards<br>_`30`: 0-Blue, `31`: 1-Blue, ..., `39`: 9-Blue_           |
| 40 - 42   | Blue action cards<br>_`40`: Skip, `41`: Reverse, `42`: Draw 2_                 |
|     43    | Blue "Wild" card                                                               |
|     44    | Blue "Wild and Draw 4" card                                                    |
| 45 - 54   | Yellow number cards<br>_`45`: 0-Yellow, `46`: 1-Yellow, ..., `54`: 9-Yellow_   |
| 55 - 57   | Yellow action cards<br>_`55`: Skip, `56`: Reverse, `57`: Draw 2_               |
|     58    | Yellow "Wild" card                                                             |
|     59    | Yellow "Wild and Draw 4" card                                                  |
|     60    | Draw                                                                           |

For example, you would use action `6` to put down a red "6" card or action `60` to draw a card. 

#### Rewards

| Winner | Loser |
| :----: | :---: |
| +1     | -1    |

#### Legal Moves

The legal moves available for each agent, found in `env.infos[agent]['legal_moves']`, are updated after each step. Taking an illegal move ends the game with a reward of -1 for the illegally moving agent and a reward of 0 for all other agents

