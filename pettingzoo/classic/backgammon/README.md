# https://github.com/dellalibera/gym-backgammon

<h1 align="center">Backgammon OpenAI Gym</h1> <br>
<p align="center">
   <img alt="Backgammon" title="Backgammon" src="./logo.png" width="350">
</p>

# Table of Contents
- [gym-backgammon](#gym_backgammon)
- [Installation](#installation)
- [Environment](#env)
    - [Observation](#observation)
    - [Actions](#actions)
    - [Reward](#reward)
    - [Starting State](#starting_state)
    - [Episode Termination](#episode_termination)
    - [Reset](#reset)
    - [Rendering](#rendering)
    - [Example](#example)
        - [Play random Agents](#play)
        - [Valid actions](#valid_actions)
- [Backgammon Versions](#versions)
- [Useful links and related works](#useful_links)
- [License](#license)

---
## <a name="gym_backgammon"></a>gym-backgammon
The backgammon game is a 2-player game that involves both the movement of the checkers and also the roll of the dice. The goal of each player is to move all of his checkers off the board.  

This repository contains a Backgammon game implementation in OpenAI Gym.   
Given the current state of the board, a roll of the dice, and the current player, it computes all the legal actions/moves (iteratively) that the current player can execute.  The legal actions are generated in a such a way that they uses the highest number of dice (if possible) for that state and player.  

---
## <a name="installation"></a>Installation
```
git clone https://github.com/dellalibera/gym-backgammon.git
cd gym-backgammon/
pip3 install -e .
```

---
## <a name="env"></a>Environment
The encoding used to represent the state is inspired by the one used by Gerald Tesauro[1].
### <a name="observation"></a>Observation
Type: Box(198)

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

### <a name="actions"></a>Actions
The valid actions that an agent can execute depend on the current state and the roll of the dice. So, there is no fixed shape for the action space.  

### <a name="reward"></a>Reward
+1 if player WHITE wins, and 0 if player BLACK wins

### <a name="starting_state"></a>Starting State
All the episodes/games start in the same [starting position](#starting_position): 
```
| 12 | 13 | 14 | 15 | 16 | 17 | BAR | 18 | 19 | 20 | 21 | 22 | 23 | OFF |
|--------Outer Board----------|     |-------P=O Home Board--------|     |
|  X |    |    |    |  O |    |     |  O |    |    |    |    |  X |     |
|  X |    |    |    |  O |    |     |  O |    |    |    |    |  X |     |
|  X |    |    |    |  O |    |     |  O |    |    |    |    |    |     |
|  X |    |    |    |    |    |     |  O |    |    |    |    |    |     |
|  X |    |    |    |    |    |     |  O |    |    |    |    |    |     |
|-----------------------------|     |-----------------------------|     |
|  O |    |    |    |    |    |     |  X |    |    |    |    |    |     |
|  O |    |    |    |    |    |     |  X |    |    |    |    |    |     |
|  O |    |    |    |  X |    |     |  X |    |    |    |    |    |     |
|  O |    |    |    |  X |    |     |  X |    |    |    |    |  O |     |
|  O |    |    |    |  X |    |     |  X |    |    |    |    |  O |     |
|--------Outer Board----------|     |-------P=X Home Board--------|     |
| 11 | 10 |  9 |  8 |  7 |  6 | BAR |  5 |  4 |  3 |  2 |  1 |  0 | OFF |
```

### <a name="episode_termination"></a>Episode Termination
1. One of the 2 players win the game
2. Episode length is greater than 10000


### <a name="reset"></a>Reset
The method `reset()` returns:
- the player that will move first (`0` for the `WHITE` player, `1` for the `BLACK` player) 
- the first roll of the dice, a tuple with the dice rolled, i.e `(1,3)` for the `BLACK` player or `(-1, -3)` for the `WHITE` player
- observation features from the starting position


### <a name="rendering"></a>Rendering
If `render(mode = 'rgb_array')` or `render(mode = 'state_pixels')` are selected, this is the output obtained (on multiple steps):
<p align="center">
   <img alt="Backgammon" title="Backgammon" src="./board.gif" width="450">
</p>

---
### <a name="example"></a>Example
#### <a name="play"></a>Play Random Agents
To run a simple example (both agents - `WHITE` and `BLACK` select an action randomly):
```
cd examples/
python3 play_random_agent.py
```
#### <a name="valid_actions"></a>Valid actions
An internal variable, `current player` is used to keep track of the player in turn (it represents the color of the player).   
To get all the valid actions:
```python
actions = env.get_valid_actions(roll)
```

The legal actions are represented as a set of tuples.    
Each action is a tuple of tuples, in the form `((source, target), (source, target))`     
Each tuple represents a move in the form `(source, target)` 

#### NOTE:
The actions of asking a double and accept/reject a double are not available.  

Given the following configuration ([starting position](#starting_position), `BLACK` player in turn, `roll = (1, 3)`):
```
| 12 | 13 | 14 | 15 | 16 | 17 | BAR | 18 | 19 | 20 | 21 | 22 | 23 | OFF |
|--------Outer Board----------|     |-------P=O Home Board--------|     |
|  X |    |    |    |  O |    |     |  O |    |    |    |    |  X |     |
|  X |    |    |    |  O |    |     |  O |    |    |    |    |  X |     |
|  X |    |    |    |  O |    |     |  O |    |    |    |    |    |     |
|  X |    |    |    |    |    |     |  O |    |    |    |    |    |     |
|  X |    |    |    |    |    |     |  O |    |    |    |    |    |     |
|-----------------------------|     |-----------------------------|     |
|  O |    |    |    |    |    |     |  X |    |    |    |    |    |     |
|  O |    |    |    |    |    |     |  X |    |    |    |    |    |     |
|  O |    |    |    |  X |    |     |  X |    |    |    |    |    |     |
|  O |    |    |    |  X |    |     |  X |    |    |    |    |  O |     |
|  O |    |    |    |  X |    |     |  X |    |    |    |    |  O |     |
|--------Outer Board----------|     |-------P=X Home Board--------|     |
| 11 | 10 |  9 |  8 |  7 |  6 | BAR |  5 |  4 |  3 |  2 |  1 |  0 | OFF |

Current player=1 (O - Black) | Roll=(1, 3)
```
The legal actions are:
```
Legal Actions:
((11, 14), (14, 15))
((0, 1), (11, 14))
((18, 19), (18, 21))
((11, 14), (18, 19))
((0, 1), (0, 3))
((0, 1), (16, 19))
((16, 17), (16, 19))
((18, 19), (19, 22))
((0, 1), (18, 21))
((16, 17), (18, 21))
((0, 3), (18, 19))
((16, 19), (18, 19))
((16, 19), (19, 20))
((0, 1), (1, 4))
((16, 17), (17, 20))
((0, 3), (16, 17))
((18, 21), (21, 22))
((0, 3), (3, 4))
((11, 14), (16, 17))
```
---

## <a name="versions"></a>Backgammon Versions 
### `backgammon-v0`
The above description refers to `backgammon-v0`.

### `backgammon-pixel-v0`
The state is represented by `(96, 96, 3)` feature vector.    
It is the only difference w.r.t `backgammon-v0`.

An example of the board representation:
<p align="center">
   <img alt="raw_pixel" title="raw_pixel" src="./raw_pixel.png" width="150">
</p>


---
## <a name="useful_links"></a>Useful links and related works
- [1][Implementation Details TD-Gammon](http://www.scholarpedia.org/article/User:Gerald_Tesauro/Proposed/Td-gammon)
- [2][Practical Issues in Temporal Difference Learning](https://papers.nips.cc/paper/465-practical-issues-in-temporal-difference-learning.pdf)
<br><br>   
- Rules of Backgammon:
    - www.bkgm.com/rules.html
    - https://en.wikipedia.org/wiki/Backgammon
    - <a name="starting_position"></a>Starting Position: http://www.bkgm.com/gloss/lookup.cgi?starting+position
    - https://bkgm.com/faq/
<br><br>   
- Other Implementation of TD-Gammon and the game of Backgammon:
    - https://github.com/TobiasVogt/TD-Gammon
    - https://github.com/millerm/TD-Gammon
    - https://github.com/fomorians/td-gammon
<br><br>
- Other Implementation of the Backgammon OpenAI Gym Environment: 
    - https://github.com/edusta/gym-backgammon

---
## <a name="license"></a>License
[MIT](https://github.com/dellalibera/gym-backgammon/blob/master/LICENSE) 