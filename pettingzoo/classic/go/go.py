# noqa
r"""
# Go

```{figure} classic_go.gif
:width: 140px
:name: go
```

This environment is part of the <a href='..'>classic environments</a>. Please read that page first for general information.

| Import             | `from pettingzoo.classic import go_v5` |
|--------------------|----------------------------------------|
| Actions            | Discrete                               |
| Parallel API       | Yes                                    |
| Manual Control     | No                                     |
| Agents             | `agents= ['black_0', 'white_0']`       |
| Agents             | 2                                      |
| Action Shape       | Discrete(362)                          |
| Action Values      | Discrete(362)                          |
| Observation Shape  | (19, 19, 3)                            |
| Observation Values | [0, 1]                                 |


Go is a board game with 2 players, black and white. The black player starts by placing a black stone at an empty board intersection. The white player follows by placing a stone of their own, aiming to either surround more territory than their opponent or capture the opponent's stones. The game
ends if both players sequentially decide to pass.

Our implementation is a wrapper for [MiniGo](https://github.com/tensorflow/minigo).

### Arguments

Go takes two optional arguments that define the board size (int) and komi compensation points (float). The default values for the board size and komi are 19 and 7.5, respectively.

``` python
go_v5.env(board_size = 19, komi = 7.5)
```

`board_size`: The length of each size of the board.

`komi`: The number of points given to white to compensate it for the disadvantage inherent to moving second. 7.5 is the standard value for Chinese tournament Go, but may not be perfectly balanced.

### Observation Space

The observation is a dictionary which contains an `'observation'` element which is the usual RL observation described below, and an  `'action_mask'` which holds the legal moves, described in the Legal Actions Mask section.


The main observation shape is a function of the board size _N_ and has a shape of (N, N, 3). The first plane, (:, :, 0), represent the stones on the board for the current player while the second plane, (:, :, 1), encodes the stones of the opponent. The third plane, (:, :, 2), is all 1 if the
current player is `black_0` or all 0 if the player is `white_0`. The state of the board is represented with the top left corner as (0, 0). For example, a (9, 9) board is
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

The legal moves available to the current agent are found in the `action_mask` element of the dictionary observation. The `action_mask` is a binary vector where each index of the vector represents whether the action is legal or not. The `action_mask` will be all zeros for any agent except the one
whose turn it is. Taking an illegal move ends the game with a reward of -1 for the illegally moving agent and a reward of 0 for all other agents.


### Action Space

Similar to the observation space, the action space is dependent on the board size _N_.

|                          Action ID                           | Description                                                  |
| :----------------------------------------------------------: | ------------------------------------------------------------ |
| <img src="https://render.githubusercontent.com/render/math?math=0 \ldots (N-1)"> | Place a stone on the 1st row of the board.<br>_`0`: (0,0), `1`: (0,1), ..., `N-1`: (0,N-1)_ |
| <img src="https://render.githubusercontent.com/render/math?math=N \ldots (2N- 1)"> | Place a stone on the 2nd row of the board.<br>_`N`: (1,0), `N+1`: (1,1), ..., `2N-1`: (1,N-1)_ |
|                             ...                              | ...                                                          |
| <img src="https://render.githubusercontent.com/render/math?math=N^2-N \ldots N^2-1"> | Place a stone on the Nth row of the board.<br>_`N^2-N`: (N-1,0), `N^2-N+1`: (N-1,1), ..., `N^2-1`: (N-1,N-1)_ |
| <img src="https://render.githubusercontent.com/render/math?math=N^2"> | Pass                                                         |

For example, you would use action `4` to place a stone on the board at the (0,3) location or action `N^2` to pass. You can transform a non-pass action `a` back into its 2D (x,y) coordinate by computing `(a//N, a%N)` The total action space is
<img src="https://render.githubusercontent.com/render/math?math=N^2 %2B 1">.

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

"""

import os
from typing import Optional

import gymnasium
import numpy as np
import pygame
from gymnasium import spaces

from pettingzoo import AECEnv
from pettingzoo.utils import wrappers
from pettingzoo.utils.agent_selector import agent_selector

from . import coords, go_base


def get_image(path):
    from os import path as os_path

    import pygame

    cwd = os_path.dirname(__file__)
    image = pygame.image.load(cwd + "/" + path)
    sfc = pygame.Surface(image.get_size(), flags=pygame.SRCALPHA)
    sfc.blit(image, (0, 0))
    return sfc


def env(**kwargs):
    env = raw_env(**kwargs)
    env = wrappers.TerminateIllegalWrapper(env, illegal_reward=-1)
    env = wrappers.AssertOutOfBoundsWrapper(env)
    env = wrappers.OrderEnforcingWrapper(env)
    return env


class raw_env(AECEnv):

    metadata = {
        "render_modes": ["human", "rgb_array"],
        "name": "go_v5",
        "is_parallelizable": False,
        "render_fps": 2,
    }

    def __init__(
        self, board_size: int = 19, komi: float = 7.5, render_mode: Optional[str] = None
    ):
        # board_size: a int, representing the board size (board has a board_size x board_size shape)
        # komi: a float, representing points given to the second player.
        super().__init__()

        self._overwrite_go_global_variables(board_size=board_size)
        self._komi = komi

        self.agents = ["black_0", "white_0"]
        self.possible_agents = self.agents[:]
        self.has_reset = False

        self.screen = None

        self.observation_spaces = self._convert_to_dict(
            [
                spaces.Dict(
                    {
                        "observation": spaces.Box(
                            low=0, high=1, shape=(self._N, self._N, 17), dtype=bool
                        ),
                        "action_mask": spaces.Box(
                            low=0,
                            high=1,
                            shape=((self._N * self._N) + 1,),
                            dtype=np.int8,
                        ),
                    }
                )
                for _ in range(self.num_agents)
            ]
        )

        self.action_spaces = self._convert_to_dict(
            [spaces.Discrete(self._N * self._N + 1) for _ in range(self.num_agents)]
        )

        self._agent_selector = agent_selector(self.agents)

        self.board_history = np.zeros((self._N, self._N, 16), dtype=bool)

        self.render_mode = render_mode

    def observation_space(self, agent):
        return self.observation_spaces[agent]

    def action_space(self, agent):
        return self.action_spaces[agent]

    def _overwrite_go_global_variables(self, board_size: int):
        self._N = board_size
        go_base.N = self._N
        go_base.ALL_COORDS = [(i, j) for i in range(self._N) for j in range(self._N)]
        go_base.EMPTY_BOARD = np.zeros([self._N, self._N], dtype=np.int8)
        go_base.NEIGHBORS = {
            (x, y): list(
                filter(
                    self._check_bounds, [(x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)]
                )
            )
            for x, y in go_base.ALL_COORDS
        }
        go_base.DIAGONALS = {
            (x, y): list(
                filter(
                    self._check_bounds,
                    [(x + 1, y + 1), (x + 1, y - 1), (x - 1, y + 1), (x - 1, y - 1)],
                )
            )
            for x, y in go_base.ALL_COORDS
        }
        return

    def _check_bounds(self, c):
        return 0 <= c[0] < self._N and 0 <= c[1] < self._N

    def _encode_player_plane(self, agent):
        if agent == self.possible_agents[0]:
            return np.zeros([self._N, self._N], dtype=bool)
        else:
            return np.ones([self._N, self._N], dtype=bool)

    def _encode_board_planes(self, agent):
        agent_factor = (
            go_base.BLACK if agent == self.possible_agents[0] else go_base.WHITE
        )
        current_agent_plane_idx = np.where(self._go.board == agent_factor)
        opponent_agent_plane_idx = np.where(self._go.board == -agent_factor)
        current_agent_plane = np.zeros([self._N, self._N], dtype=bool)
        opponent_agent_plane = np.zeros([self._N, self._N], dtype=bool)
        current_agent_plane[current_agent_plane_idx] = 1
        opponent_agent_plane[opponent_agent_plane_idx] = 1
        return current_agent_plane, opponent_agent_plane

    def _int_to_name(self, ind):
        return self.possible_agents[ind]

    def _name_to_int(self, name):
        return self.possible_agents.index(name)

    def _convert_to_dict(self, list_of_list):
        return dict(zip(self.possible_agents, list_of_list))

    def _encode_legal_actions(self, actions):
        return np.where(actions == 1)[0]

    def _encode_rewards(self, result):
        return [1, -1] if result == 1 else [-1, 1]

    def observe(self, agent):
        current_agent_plane, opponent_agent_plane = self._encode_board_planes(agent)
        player_plane = self._encode_player_plane(agent)

        observation = np.dstack((self.board_history, player_plane))

        legal_moves = self.next_legal_moves if agent == self.agent_selection else []
        action_mask = np.zeros((self._N * self._N) + 1, "int8")
        for i in legal_moves:
            action_mask[i] = 1

        return {"observation": observation, "action_mask": action_mask}

    def step(self, action):
        if (
            self.terminations[self.agent_selection]
            or self.truncations[self.agent_selection]
        ):
            return self._was_dead_step(action)
        self._go = self._go.play_move(coords.from_flat(action))
        self._last_obs = self.observe(self.agent_selection)
        current_agent_plane, opponent_agent_plane = self._encode_board_planes(
            self.agent_selection
        )
        self.board_history = np.dstack(
            (current_agent_plane, opponent_agent_plane, self.board_history[:, :, :-2])
        )
        next_player = self._agent_selector.next()
        if self._go.is_game_over():
            self.terminations = self._convert_to_dict(
                [True for _ in range(self.num_agents)]
            )
            self.rewards = self._convert_to_dict(
                self._encode_rewards(self._go.result())
            )
            self.next_legal_moves = [self._N * self._N]
        else:
            self.next_legal_moves = self._encode_legal_actions(
                self._go.all_legal_moves()
            )
        self.agent_selection = (
            next_player if next_player else self._agent_selector.next()
        )
        self._accumulate_rewards()

        if self.render_mode == "human":
            self.render()

    def reset(self, seed=None, return_info=False, options=None):
        self.has_reset = True
        self._go = go_base.Position(board=None, komi=self._komi)

        self.agents = self.possible_agents[:]
        self._agent_selector.reinit(self.agents)
        self.agent_selection = self._agent_selector.reset()
        self._cumulative_rewards = self._convert_to_dict(np.array([0.0, 0.0]))
        self.rewards = self._convert_to_dict(np.array([0.0, 0.0]))
        self.terminations = self._convert_to_dict(
            [False for _ in range(self.num_agents)]
        )
        self.truncations = self._convert_to_dict(
            [False for _ in range(self.num_agents)]
        )
        self.infos = self._convert_to_dict([{} for _ in range(self.num_agents)])
        self.next_legal_moves = self._encode_legal_actions(self._go.all_legal_moves())
        self._last_obs = self.observe(self.agents[0])
        self.board_history = np.zeros((self._N, self._N, 16), dtype=bool)

    def render(self):
        if self.render_mode is None:
            gymnasium.logger.warn(
                "You are calling render method without specifying any render mode."
            )
            return

        screen_width = 1026
        screen_height = 1026

        if self.screen is None:
            if self.render_mode == "human":
                pygame.init()
                self.screen = pygame.display.set_mode((screen_width, screen_height))
            else:
                self.screen = pygame.Surface((screen_width, screen_height))
        if self.render_mode == "human":
            pygame.event.get()

        size = go_base.N

        # Load and scale all of the necessary images
        tile_size = (screen_width) / size

        black_stone = get_image(os.path.join("img", "GoBlackPiece.png"))
        black_stone = pygame.transform.scale(
            black_stone, (int(tile_size * (5 / 6)), int(tile_size * (5 / 6)))
        )

        white_stone = get_image(os.path.join("img", "GoWhitePiece.png"))
        white_stone = pygame.transform.scale(
            white_stone, (int(tile_size * (5 / 6)), int(tile_size * (5 / 6)))
        )

        tile_img = get_image(os.path.join("img", "GO_Tile0.png"))
        tile_img = pygame.transform.scale(
            tile_img, ((int(tile_size * (7 / 6))), int(tile_size * (7 / 6)))
        )

        # blit board tiles
        for i in range(1, size - 1):
            for j in range(1, size - 1):
                self.screen.blit(tile_img, ((i * (tile_size)), int(j) * (tile_size)))

        for i in range(1, 9):
            tile_img = get_image(os.path.join("img", "GO_Tile" + str(i) + ".png"))
            tile_img = pygame.transform.scale(
                tile_img, ((int(tile_size * (7 / 6))), int(tile_size * (7 / 6)))
            )
            for j in range(1, size - 1):
                if i == 1:
                    self.screen.blit(tile_img, (0, int(j) * (tile_size)))
                elif i == 2:
                    self.screen.blit(tile_img, ((int(j) * (tile_size)), 0))
                elif i == 3:
                    self.screen.blit(
                        tile_img, ((size - 1) * (tile_size), int(j) * (tile_size))
                    )
                elif i == 4:
                    self.screen.blit(
                        tile_img, ((int(j) * (tile_size)), (size - 1) * (tile_size))
                    )
            if i == 5:
                self.screen.blit(tile_img, (0, 0))
            elif i == 6:
                self.screen.blit(tile_img, ((size - 1) * (tile_size), 0))
            elif i == 7:
                self.screen.blit(
                    tile_img, ((size - 1) * (tile_size), (size - 1) * (tile_size))
                )
            elif i == 8:
                self.screen.blit(tile_img, (0, (size - 1) * (tile_size)))

        offset = tile_size * (1 / 6)
        # Blit the necessary chips and their positions
        for i in range(0, size):
            for j in range(0, size):
                if self._go.board[i][j] == go_base.BLACK:
                    self.screen.blit(
                        black_stone,
                        ((i * (tile_size) + offset), int(j) * (tile_size) + offset),
                    )
                elif self._go.board[i][j] == go_base.WHITE:
                    self.screen.blit(
                        white_stone,
                        ((i * (tile_size) + offset), int(j) * (tile_size) + offset),
                    )

        if self.render_mode == "human":
            pygame.display.update()

        observation = np.array(pygame.surfarray.pixels3d(self.screen))

        return (
            np.transpose(observation, axes=(1, 0, 2))
            if self.render_mode == "rgb_array"
            else None
        )

    def close(self):
        pass
