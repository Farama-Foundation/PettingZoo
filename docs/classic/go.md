---
actions: "Discrete"
title: "Go"
agents: "2"
manual-control: "No"
action-shape: "Discrete(362)"
action-values: "Discrete(362)"
observation-shape: "(19, 19, 3)"
observation-values: "[0, 1]"
import: "from pettingzoo.classic import go_v5"
agent-labels: "agents= ['black_0', 'white_0']"
---

<div class="docu-info" markdown="1">
{% include info_box.md %}
</div>

<div class="docu-content" markdown="1">
<div class="appear_big env-title" markdown="1">
{% include env_icon.md %}
## {{page.title}}
</div>




Go is a board game with 2 players, black and white. The black player starts by placing a black stone at an empty board intersection. The white player follows by placing a stone of their own, aiming to either surround more territory than their opponent or capture the opponent's stones. The game ends if both players sequentially decide to pass.

Our implementation is a wrapper for [MiniGo](https://github.com/tensorflow/minigo).

### Arguments

Go takes two optional arguments that define the board size (int) and komi compensation points (float). The default values for the board size and komi are 19 and 7.5, respectively.

``` python
go_v5.env(board_size = 19, komi = 7.5)
```

`board_size`: The length of each size of the board.

`komi`: The number of points given to white to compensate it for the disadvantage inherent to moving second. 7.5 is the standard value for Chinese tournament Go, but may not be perfectly balanced.

### Observation Space

The observation is a dictionary which contains an `'obs'` element which is the usual RL observation described below, and an  `'action_mask'` which holds the legal moves, described in the Legal Actions Mask section.


The main observation shape is a function of the board size _N_ and has a shape of (N, N, 3). The first plane, (:, :, 0), represent the stones on the board for the current player while the second plane, (:, :, 1), encodes the stones of the opponent. The third plane, (:, :, 2), is all 1 if the current player is `black_0` or all 0 if the player is `white_0`. The state of the board is represented with the top left corner as (0, 0). For example, a (9, 9) board is  
```
   0 1 2 3 4 5 6 7 8
 0 . . . . . . . . .  0
 1 . . . . . . . . .  1
 2 . . . . . . . . .  2
 3 . . . . . . . . .  3
 4 . . . . . . . . .  4
 5 . . . . . . . . .  5
 6 . . . . . . . . .  6
 7 . . . . . . . . .  7
 8 . . . . . . . . .  8
   0 1 2 3 4 5 6 7 8
```

|  Plane  | Description                                               |
|:-------:|-----------------------------------------------------------|
|    0    | Current Player's stones<br>_'`0`: no stone, `1`: stone_   |
|    1    | Opponent Player's stones<br>_'`0`: no stone, `1`: stone_  |
|    2    | Player<br>_'`0`: white, `1`: black_                       |

While rendering, the board coordinate system is [GTP](http://www.lysator.liu.se/~gunnar/gtp/).


#### Legal Actions Mask

The legal moves available to the current agent are found in the `action_mask` element of the dictionary observation. The `action_mask` is a binary vector where each index of the vector represents whether the action is legal or not. The `action_mask` will be all zeros for any agent except the one whose turn it is. Taking an illegal move ends the game with a reward of -1 for the illegally moving agent and a reward of 0 for all other agents.


### Action Space

Similar to the observation space, the action space is dependent on the board size _N_.

|                          Action ID                           | Description                                                  |
| :----------------------------------------------------------: | ------------------------------------------------------------ |
| <img src="https://render.githubusercontent.com/render/math?math=0 \ldots (N-1)"> | Place a stone on the 1st row of the board.<br>_`0`: (0,0), `1`: (0,1), ..., `N-1`: (0,N-1)_ |
| <img src="https://render.githubusercontent.com/render/math?math=N \ldots (2N- 1)"> | Place a stone on the 2nd row of the board.<br>_`N`: (1,0), `N+1`: (1,1), ..., `2N-1`: (1,N-1)_ |
|                             ...                              | ...                                                          |
| <img src="https://render.githubusercontent.com/render/math?math=N^2-N \ldots N^2-1"> | Place a stone on the Nth row of the board.<br>_`N^2-N`: (N-1,0), `N^2-N+1`: (N-1,1), ..., `N^2-1`: (N-1,N-1)_ |
| <img src="https://render.githubusercontent.com/render/math?math=N^2"> | Pass                                                         |

For example, you would use action `4` to place a stone on the board at the (0,3) location or action `N^2` to pass. You can transform a non-pass action `a` back into its 2D (x,y) coordinate by computing `(a//N, a%N)` The total action space is <img src="https://render.githubusercontent.com/render/math?math=N^2 %2B 1">.

### Rewards

| Winner | Loser |
| :----: | :---: |
| +1     | -1    |

### Version History

* v5: Changed observation space to proper AlphaZero style frame stacking (1.11.0)
* v4: Fixed bug in how black and white pieces were saved in observation space (1.10.0)
* v3: Fixed bug in arbitrary calls to observe() (1.8.0)
* v2: Legal action mask in observation replaced illegal move list in infos (1.5.0)
* v1: Bumped version of all environments due to adoption of new agent iteration scheme where all agents are iterated over after they are done (1.4.0)
* v0: Initial versions release (1.0.0)
</div>
