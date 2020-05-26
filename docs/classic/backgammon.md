### Backgammon

This game part of the [classic games](../classic.md), please visit that page first for general information about these games.

| Actions | Agents | Manual Control | Action Shape | Action Values | Observation Shape | Observation Values | Num States |
|----------|---------|----------------|--------------|---------------|-------------------|--------------------|------------|
| Discrete           | 2       | No      | Discrete($26^2 * 2 + 1$)              | Discrete( $26^2 * 2 + 1$)            | (198,)             | [0, 7.5]                 | 10^26                  |

`from pettingzoo.classic import backgammon_v0`

`agents= ['player_0', 'player_1']`


Backgammon is a 2-player turn based board game. Players take turns rolling 2 dice and moving checkers forward according to those rolls. A player wins if they are the first to remove all of their checkers from the board.

This environment uses [gym-backgammon](https://github.com/dellalibera/gym-backgammon)'s implementation of backgammon.

The rules of backgammon can be found [here.](https://www.bkgm.com/rules.html)

#### Observation Space
The observation space has shape (198,). Entries 0-97 represent the positions of any white checkers, entries 98-195 represent the positions of any black checkers, and entries 196-197 encode the current player.

| Num       | Observation                                                         | Min  | Max  |
| --------- | -----------------------------------------------------------------   | ---- | ---- |
| 0         | WHITE - 1st point, 1st component                                    | 0.0  | 1.0  |
| 1         | WHITE - 1st point, 2nd component                                    | 0.0  | 1.0  |
| 2         | WHITE - 1st point, 3rd component                                    | 0.0  | 1.0  |
| 3         | WHITE - 1st point, 4th component                                    | 0.0  | 6.0  |
| 4         | WHITE - 2nd point, 1st component                                    | 0.0  | 1.0  |
| 5         | WHITE - 2nd point, 2nd component                                    | 0.0  | 1.0  |
| 6         | WHITE - 2nd point, 3rd component                                    | 0.0  | 1.0  |
| 7         | WHITE - 2nd point, 4th component                                    | 0.0  | 6.0  |
| ...       |                                                                     |      |      |
| 92        | WHITE - 24th point, 1st component                                   | 0.0  | 1.0  |
| 93        | WHITE - 24th point, 2nd component                                   | 0.0  | 1.0  |
| 94        | WHITE - 24th point, 3rd component                                   | 0.0  | 1.0  |
| 95        | WHITE - 24th point, 4th component                                   | 0.0  | 6.0  |
| 96        | WHITE - BAR checkers                                                | 0.0  | 7.5  |
| 97        | WHITE - OFF bar checkers                                            | 0.0  | 1.0  |
| 98        | BLACK - 1st point, 1st component                                    | 0.0  | 1.0  |
| 99        | BLACK - 1st point, 2nd component                                    | 0.0  | 1.0  |
| 100       | BLACK - 1st point, 3rd component                                    | 0.0  | 1.0  |
| 101       | BLACK - 1st point, 4th component                                    | 0.0  | 6.0  |
| ...       |                                                                     |      |      |
| 190       | BLACK - 24th point, 1st component                                   | 0.0  | 1.0  |
| 191       | BLACK - 24th point, 2nd component                                   | 0.0  | 1.0  |
| 192       | BLACK - 24th point, 3rd component                                   | 0.0  | 1.0  |
| 193       | BLACK - 24th point, 4th component                                   | 0.0  | 6.0  |
| 194       | BLACK - BAR checkers                                                | 0.0  | 7.5  |
| 195       | BLACK - OFF bar checkers                                            | 0.0  | 1.0  |
| 196 - 197 | Current player                                                      | 0.0  | 1.0  |

Encoding of a single point (it indicates the number of checkers in that point):

| Checkers | Encoding                                |           
| -------- | --------------------------------------- |
| 0        | [0.0, 0.0, 0.0, 0.0]                    |
| 1        | [1.0, 0.0, 0.0, 0.0]                    |
| 2        | [1.0, 1.0, 0.0, 0.0]                    |
| >= 3     | [1.0, 1.0, 1.0, (checkers - 3.0) / 2.0] |

Encoding of BAR checkers:

| Checkers | Encoding             |           
| -------- | -------------------- |
| 0 - 14   | [bar_checkers / 2.0] |

Encoding of OFF bar checkers:

| Checkers | Encoding              |           
| -------- | --------------------- |
| 0 - 14   | [off_checkers / 15.0] |

Encoding of the current player:

| Player  | Encoding   |           
| ------- | ---------- |
| WHITE   | [1.0, 0.0] |
| BLACK   | [0.0, 1.0] |

#### Action Space
The action space for this environment is Discrete($26^2 * 2 + 1$).

Each action number encodes the two source locations to move checkers from in base 26.

Actions in [$0$, $26^ 2 -1$] use the low dice roll first, and actions in [$26^2$, $2*26 ^2 - 1$] use the high dice roll first.

The 'do nothing' action is $26^2*2$

| Action ID  | First Source ID  | Second Source ID|  First Roll Used | Second Roll Used |         
| ------- | ---------- |---------- |---------- |---------- |
| 0 to $26^ 2 -1$   | action % $26$ | action / $26$ | Low Roll | High Roll
| $26^2$ to $26^2*2 -1$   | (action $- 26^2$) % $26$ |(action $- 26^2$) / $26$ | High Roll | Low Roll
| $26^2*2$   | None |None | None | None

The location on the board can be found from the Location ID, which is either the source ID, or the destination ID (source ID + Roll).

| Location ID (S) | Board Location |
| ------- |  ------- |
| <1 | White's bear off location|
|1 to 24 | Point number S-1|
|25 | Bar|
|>25 | Black's bear off location|

#### Rewards

| Winner | Loser |
| :----: | :---: |
| +1     | -1    |

#### Legal Moves

The legal moves available for each agent, found in `env.infos[agent]['legal_moves']`, are updated after each step. Taking an illegal move ends the game with a reward of -1 for the illegally moving agent and a reward of 0 for 
