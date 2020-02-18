# https://github.com/qmchenry/gym-chess


# gym-chess

A simple chess environment for gym. It computes all available moves, including castling, *en-passant*, pawn promotions and 3-fold repetition draws. 

<table style="text-align:center;border-spacing:0pt;font-family:'Arial Unicode MS'; border-collapse:collapse; border-color: black; border-style: solid; border-width: 0pt 0pt 0pt 0pt">
<tr>
<td style="width:12pt">8</td>
<td style="width:24pt; height:24pt; border-collapse:collapse; border-color: black; border-style: solid; border-width: 1pt 0pt 0pt 1pt"><span style="font-size:150%;">♜</span></td>
<td style="width:24pt; height:24pt; border-collapse:collapse; border-color: black; border-style: solid; border-width: 1pt 0pt 0pt 0pt" bgcolor="silver"><span style="font-size:150%;">♞</span></td>
<td style="width:24pt; height:24pt; border-collapse:collapse; border-color: black; border-style: solid; border-width: 1pt 0pt 0pt 0pt"><span style="font-size:150%;">♝</span></td>
<td style="width:24pt; height:24pt; border-collapse:collapse; border-color: black; border-style: solid; border-width: 1pt 0pt 0pt 0pt" bgcolor="silver"><span style="font-size:150%;">♛</span></td>
<td style="width:24pt; height:24pt; border-collapse:collapse; border-color: black; border-style: solid; border-width: 1pt 0pt 0pt 0pt"><span style="font-size:150%;">♚</span></td>
<td style="width:24pt; height:24pt; border-collapse:collapse; border-color: black; border-style: solid; border-width: 1pt 0pt 0pt 0pt" bgcolor="silver"><span style="font-size:150%;">♝</span></td>
<td style="width:24pt; height:24pt; border-collapse:collapse; border-color: black; border-style: solid; border-width: 1pt 0pt 0pt 0pt"><span style="font-size:150%;">♞</span></td>
<td style="width:24pt; height:24pt; border-collapse:collapse; border-color: black; border-style: solid; border-width: 1pt 1pt 0pt 0pt" bgcolor="silver"><span style="font-size:150%;">♜</span></td>
</tr>
<tr>
<td style="width:12pt">7</td>
<td style="width:24pt; height:24pt; border-collapse:collapse; border-color: black; border-style: solid; border-width: 0pt 0pt 0pt 1pt" bgcolor="silver"><span style="font-size:150%;">♟</span></td>
<td style="width:24pt; height:24pt;"><span style="font-size:150%;">♟</span></td>
<td style="width:24pt; height:24pt;" bgcolor="silver"><span style="font-size:150%;">♟</span></td>
<td style="width:24pt; height:24pt;"><span style="font-size:150%;">♟</span></td>
<td style="width:24pt; height:24pt;" bgcolor="silver"><span style="font-size:150%;">♟</span></td>
<td style="width:24pt; height:24pt;"><span style="font-size:150%;">♟</span></td>
<td style="width:24pt; height:24pt;" bgcolor="silver"><span style="font-size:150%;">♟</span></td>
<td style="width:24pt; height:24pt; border-collapse:collapse; border-color: black; border-style: solid; border-width: 0pt 1pt 0pt 0pt"><span style="font-size:150%;">♟</span></td>
</tr>
<tr>
<td style="width:12pt">6</td>
<td style="width:24pt; height:24pt; border-collapse:collapse; border-color: black; border-style: solid; border-width: 0pt 0pt 0pt 1pt"><span style="font-size:150%;"><br /></span></td>
<td style="width:24pt; height:24pt;" bgcolor="silver"></td>
<td style="width:24pt; height:24pt;"></td>
<td style="width:24pt; height:24pt;" bgcolor="silver"></td>
<td style="width:24pt; height:24pt;"></td>
<td style="width:24pt; height:24pt;" bgcolor="silver"></td>
<td style="width:24pt; height:24pt;"></td>
<td style="width:24pt; height:24pt; border-collapse:collapse; border-color: black; border-style: solid; border-width: 0pt 1pt 0pt 0pt" bgcolor="silver"></td>
</tr>
<tr>
<td style="width:12pt">5</td>
<td style="width:24pt; height:24pt; border-collapse:collapse; border-color: black; border-style: solid; border-width: 0pt 0pt 0pt 1pt" bgcolor="silver"><span style="font-size:150%;"><br /></span></td>
<td style="width:24pt; height:24pt;"></td>
<td style="width:24pt; height:24pt;" bgcolor="silver"></td>
<td style="width:24pt; height:24pt;"></td>
<td style="width:24pt; height:24pt;" bgcolor="silver"></td>
<td style="width:24pt; height:24pt;"></td>
<td style="width:24pt; height:24pt;" bgcolor="silver"></td>
<td style="width:24pt; height:24pt; border-collapse:collapse; border-color: black; border-style: solid; border-width: 0pt 1pt 0pt 0pt"></td>
</tr>
<tr>
<td style="width:12pt">4</td>
<td style="width:24pt; height:24pt; border-collapse:collapse; border-color: black; border-style: solid; border-width: 0pt 0pt 0pt 1pt"><span style="font-size:150%;"><br /></span></td>
<td style="width:24pt; height:24pt;" bgcolor="silver"></td>
<td style="width:24pt; height:24pt;"></td>
<td style="width:24pt; height:24pt;" bgcolor="silver"></td>
<td style="width:24pt; height:24pt;"></td>
<td style="width:24pt; height:24pt;" bgcolor="silver"></td>
<td style="width:24pt; height:24pt;"></td>
<td style="width:24pt; height:24pt; border-collapse:collapse; border-color: black; border-style: solid; border-width: 0pt 1pt 0pt 0pt" bgcolor="silver"></td>
</tr>
<tr>
<td style="width:12pt">3</td>
<td style="width:24pt; height:24pt; border-collapse:collapse; border-color: black; border-style: solid; border-width: 0pt 0pt 0pt 1pt" bgcolor="silver"><span style="font-size:150%;"><br /></span></td>
<td style="width:24pt; height:24pt;"></td>
<td style="width:24pt; height:24pt;" bgcolor="silver"></td>
<td style="width:24pt; height:24pt;"></td>
<td style="width:24pt; height:24pt;" bgcolor="silver"></td>
<td style="width:24pt; height:24pt;"></td>
<td style="width:24pt; height:24pt;" bgcolor="silver"></td>
<td style="width:24pt; height:24pt; border-collapse:collapse; border-color: black; border-style: solid; border-width: 0pt 1pt 0pt 0pt"></td>
</tr>
<tr>
<td style="width:12pt">2</td>
<td style="width:24pt; height:24pt; border-collapse:collapse; border-color: black; border-style: solid; border-width: 0pt 0pt 0pt 1pt"><span style="font-size:150%;">♙</span></td>
<td style="width:24pt; height:24pt;" bgcolor="silver"><span style="font-size:150%;">♙</span></td>
<td style="width:24pt; height:24pt;"><span style="font-size:150%;">♙</span></td>
<td style="width:24pt; height:24pt;" bgcolor="silver"><span style="font-size:150%;">♙</span></td>
<td style="width:24pt; height:24pt;"><span style="font-size:150%;">♙</span></td>
<td style="width:24pt; height:24pt;" bgcolor="silver"><span style="font-size:150%;">♙</span></td>
<td style="width:24pt; height:24pt;"><span style="font-size:150%;">♙</span></td>
<td style="width:24pt; height:24pt; border-collapse:collapse; border-color: black; border-style: solid; border-width: 0pt 1pt 0pt 0pt" bgcolor="silver"><span style="font-size:150%;">♙</span></td>
</tr>
<tr>
<td style="width:12pt">1</td>
<td style="width:24pt; height:24pt; border-collapse:collapse; border-color: black; border-style: solid; border-width: 0pt 0pt 1pt 1pt" bgcolor="silver"><span style="font-size:150%;">♖</span></td>
<td style="width:24pt; height:24pt; border-collapse:collapse; border-color: black; border-style: solid; border-width: 0pt 0pt 1pt 0pt"><span style="font-size:150%;">♘</span></td>
<td style="width:24pt; height:24pt; border-collapse:collapse; border-color: black; border-style: solid; border-width: 0pt 0pt 1pt 0pt" bgcolor="silver"><span style="font-size:150%;">♗</span></td>
<td style="width:24pt; height:24pt; border-collapse:collapse; border-color: black; border-style: solid; border-width: 0pt 0pt 1pt 0pt"><span style="font-size:150%;">♕</span></td>
<td style="width:24pt; height:24pt; border-collapse:collapse; border-color: black; border-style: solid; border-width: 0pt 0pt 1pt 0pt" bgcolor="silver"><span style="font-size:150%;">♔</span></td>
<td style="width:24pt; height:24pt; border-collapse:collapse; border-color: black; border-style: solid; border-width: 0pt 0pt 1pt 0pt"><span style="font-size:150%;">♗</span></td>
<td style="width:24pt; height:24pt; border-collapse:collapse; border-color: black; border-style: solid; border-width: 0pt 0pt 1pt 0pt" bgcolor="silver"><span style="font-size:150%;">♘</span></td>
<td style="width:24pt; height:24pt; border-collapse:collapse; border-color: black; border-style: solid; border-width: 0pt 1pt 1pt 0pt"><span style="font-size:150%;">♖</span></td>
</tr>
<tr>
<td></td>
<td>a</td>
<td>b</td>
<td>c</td>
<td>d</td>
<td>e</td>
<td>f</td>
<td>g</td>
<td>h</td>
</tr>
</table>

### Setup

Install the environment:

``` python

pip install -e .  

```

Play against yourself or against a random bot.

``` python

import gym
import gym_chess

env = gym.make('ChessVsRandomBot-v0')
env = gym.make('ChessVsSelf-v0')

```

### Play

You can either get available moves and convert them into the action space, or get the available actions directly. 

``` python 

import random

# moves
moves = env.get_possible_moves(state, player)
m = random.choice(moves)
action = env.move_to_actions(m)

# actions
actions = env.get_possible_actions(state, player)
action = random.choice(actions)


```


A move is a dictionary that holds the id of the piece (from 1 to 16 for white and -1 to -16 for black), its current position and its new position. 

``` python

move = {
    'piece_id': <int>,
    'pos': [<int>,<int>],
    'new_pos': [<int>,<int>]
}

```

NB: when a move is converted to an action and vice-versa, the `'pos'` attribute is dropped (it doesn't provide any useful information since the current position of a given piece is recorded in the current state). 


Pass an action to the environment and retrieve the `new state`, `reward`, `done` and `info`:

``` python 

state, reward, done, __ = env.step(action)

```

Reset the environment:

``` python 

initial_state = env.reset()

```

### Visualise the chess board

Visualise the current state of the chess game:

``` python

env.render()

```

Show the moves that a piece can make given a set of moves (by any/all pieces on the board)

``` python

# Player 1 moves
piece = 6 # white queen
env.render_moves(state, piece, moves, mode='human')

```

You can also retrieve the list of squares that pieces are attacking and defending by specifying the "attack" option:

``` python

attacking_moves = env.get_possible_moves(state, player, attack=True)

```
