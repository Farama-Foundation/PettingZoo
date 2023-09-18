# noqa: D212, D415
"""
# Texas Hold'em No Limit

```{figure} classic_texas_holdem_no_limit.gif
:width: 140px
:name: texas_holdem_no_limit
```

This environment is part of the <a href='..'>classic environments</a>. Please read that page first for general information.

| Import             | `from pettingzoo.classic import texas_holdem_no_limit_v6` |
|--------------------|-----------------------------------------------------------|
| Actions            | Discrete                                                  |
| Parallel API       | Yes                                                       |
| Manual Control     | No                                                        |
| Agents             | `agents= ['player_0', 'player_1']`                        |
| Agents             | 2                                                         |
| Action Shape       | Discrete(5)                                               |
| Action Values      | Discrete(5)                                               |
| Observation Shape  | (54,)                                                     |
| Observation Values | [0, 100]                                                  |


Texas Hold'em No Limit is a variation of Texas Hold'em where there is no limit on the amount of each raise or the number of raises.

Our implementation wraps [RLCard](http://rlcard.org/games.html#no-limit-texas-hold-em) and you can refer to its documentation for additional details. Please cite their work if you use this game in research.

### Arguments

``` python
texas_holdem_no_limit_v6.env(num_players=2)
```

`num_players`: Sets the number of players in the game. Minimum is 2.


Texas Hold'em is a poker game involving 2 players and a regular 52 cards deck. At the beginning, both players get two cards. After betting, three community cards are shown and another round follows. At any time, a player could fold and the game will end. The winner will receive +1 as a reward and
the loser will get -1. This is an implementation of the standard limited version of Texas Hold'm, sometimes referred to as 'Limit Texas Hold'em'.

Our implementation wraps [RLCard](http://rlcard.org/games.html#limit-texas-hold-em) and you can refer to its documentation for additional details. Please cite their work if you use this game in research.


### Observation Space

The observation is a dictionary which contains an `'observation'` element which is the usual RL observation described below, and an  `'action_mask'` which holds the legal moves, described in the Legal Actions Mask section.

The main observation space is similar to Texas Hold'em. The first 52 entries represent the union of the current player's hand and the community cards.

|  Index  | Description                                  |  Values  |
|:-------:|----------------------------------------------|:--------:|
|  0 - 12 | Spades<br>_`0`: A, `1`: 2, ..., `12`: K_     |  [0, 1]  |
| 13 - 25 | Hearts<br>_`13`: A, `14`: 2, ..., `25`: K_   |  [0, 1]  |
| 26 - 38 | Diamonds<br>_`26`: A, `27`: 2, ..., `38`: K_ |  [0, 1]  |
| 39 - 51 | Clubs<br>_`39`: A, `40`: 2, ..., `51`: K_    |  [0, 1]  |
|    52   | Number of Chips of player_0                  | [0, 100] |
|    53   | Number of Chips of player_1                  | [0, 100] |

#### Legal Actions Mask

The legal moves available to the current agent are found in the `action_mask` element of the dictionary observation. The `action_mask` is a binary vector where each index of the vector represents whether the action is legal or not. The `action_mask` will be all zeros for any agent except the one
whose turn it is. Taking an illegal move ends the game with a reward of -1 for the illegally moving agent and a reward of 0 for all other agents.

### Action Space

| Action ID   |     Action         |
| ----------- | :----------------- |
| 0           | Fold               |
| 1           | Check & Call       |
| 2           | Raise Half Pot     |
| 3           | Raise Full Pot     |
| 4           | All In             |

### Rewards

| Winner          | Loser           |
| :-------------: | :-------------: |
| +raised chips/2 | -raised chips/2 |

### Version History

* v6: Upgrade to RLCard 1.0.5, fixes to the action space as ACPC (1.12.0)
* v5: Upgrade to RLCard 1.0.4, fixes to rewards with greater than 2 players (1.11.1)
* v4: Upgrade to RLCard 1.0.3 (1.11.0)
* v3: Fixed bug in arbitrary calls to observe() (1.8.0)
* v2: Bumped RLCard version, bug fixes, legal action mask in observation replaced illegal move list in infos (1.5.0)
* v1: Bumped RLCard version, fixed observation space, adopted new agent iteration scheme where all agents are iterated over after they are done (1.4.0)
* v0: Initial versions release (1.0.0)

"""
from __future__ import annotations

import os

import gymnasium
import numpy as np
import pygame
from gymnasium import spaces
from gymnasium.utils import EzPickle

from pettingzoo.classic.rlcard_envs.rlcard_base import RLCardBase
from pettingzoo.utils import wrappers

# Pixel art from Mariia Khmelnytska (https://www.123rf.com/photo_104453049_stock-vector-pixel-art-playing-cards-standart-deck-vector-set.html)


def get_image(path):
    from os import path as os_path

    cwd = os_path.dirname(__file__)
    image = pygame.image.load(cwd + "/" + path)
    return image


def get_font(path, size):
    from os import path as os_path

    cwd = os_path.dirname(__file__)
    font = pygame.font.Font((cwd + "/" + path), size)
    return font


def env(**kwargs):
    env = raw_env(**kwargs)
    env = wrappers.TerminateIllegalWrapper(env, illegal_reward=-1)
    env = wrappers.AssertOutOfBoundsWrapper(env)
    env = wrappers.OrderEnforcingWrapper(env)
    return env


class raw_env(RLCardBase, EzPickle):
    metadata = {
        "render_modes": ["human", "rgb_array"],
        "name": "texas_holdem_no_limit_v6",
        "is_parallelizable": False,
        "render_fps": 1,
    }

    def __init__(
        self,
        num_players: int = 2,
        render_mode: str | None = None,
        screen_height: int | None = 1000,
    ):
        EzPickle.__init__(self, num_players, render_mode, screen_height)
        super().__init__("no-limit-holdem", num_players, (54,))
        self.observation_spaces = self._convert_to_dict(
            [
                spaces.Dict(
                    {
                        "observation": spaces.Box(
                            low=np.zeros(
                                54,
                            ),
                            high=np.append(
                                np.ones(
                                    52,
                                ),
                                [100, 100],
                            ),
                            dtype=np.float32,
                        ),
                        "action_mask": spaces.Box(
                            low=0, high=1, shape=(self.env.num_actions,), dtype=np.int8
                        ),
                    }
                )
                for _ in range(self.num_agents)
            ]
        )

        self.render_mode = render_mode
        self.screen_height = screen_height

        if self.render_mode == "human":
            self.clock = pygame.time.Clock()

    def step(self, action):
        super().step(action)

        if self.render_mode == "human":
            self.render()

    def render(self):
        if self.render_mode is None:
            gymnasium.logger.warn(
                "You are calling render method without specifying any render mode."
            )
            return

        def calculate_width(self, screen_width, i):
            return int(
                (
                    screen_width
                    / (np.ceil(len(self.possible_agents) / 2) + 1)
                    * np.ceil((i + 1) / 2)
                )
                + (tile_size * 33 / 616)
            )

        def calculate_offset(hand, j, tile_size):
            return int(
                (len(hand) * (tile_size * 23 / 56)) - ((j) * (tile_size * 23 / 28))
            )

        def calculate_height(screen_height, divisor, multiplier, tile_size, offset):
            return int(multiplier * screen_height / divisor + tile_size * offset)

        screen_height = self.screen_height
        screen_width = int(
            screen_height * (1 / 20)
            + np.ceil(len(self.possible_agents) / 2) * (screen_height * 12 / 20)
        )

        if self.screen is None:
            pygame.init()

            if self.render_mode == "human":
                self.screen = pygame.display.set_mode((screen_width, screen_height))
                pygame.display.set_caption("Texas Hold'em No Limit")
            else:
                self.screen = pygame.Surface((screen_width, screen_height))

        # Setup dimensions for card size and setup for colors
        tile_size = screen_height * 2 / 10

        bg_color = (7, 99, 36)
        white = (255, 255, 255)
        self.screen.fill(bg_color)

        chips = {
            0: {"value": 10000, "img": "ChipOrange.png", "number": 0},
            1: {"value": 5000, "img": "ChipPink.png", "number": 0},
            2: {"value": 1000, "img": "ChipYellow.png", "number": 0},
            3: {"value": 100, "img": "ChipBlack.png", "number": 0},
            4: {"value": 50, "img": "ChipBlue.png", "number": 0},
            5: {"value": 25, "img": "ChipGreen.png", "number": 0},
            6: {"value": 10, "img": "ChipLightBlue.png", "number": 0},
            7: {"value": 5, "img": "ChipRed.png", "number": 0},
            8: {"value": 1, "img": "ChipWhite.png", "number": 0},
        }

        # Load and blit all images for each card in each player's hand
        for i, player in enumerate(self.possible_agents):
            state = self.env.game.get_state(self._name_to_int(player))
            for j, card in enumerate(state["hand"]):
                # Load specified card
                card_img = get_image(os.path.join("img", card + ".png"))
                card_img = pygame.transform.scale(
                    card_img, (int(tile_size * (142 / 197)), int(tile_size))
                )
                # Players with even id go above public cards
                if i % 2 == 0:
                    self.screen.blit(
                        card_img,
                        (
                            (
                                calculate_width(self, screen_width, i)
                                - calculate_offset(state["hand"], j, tile_size)
                                - tile_size
                                * (8 / 10)
                                * (1 - np.ceil(i / 2))
                                * (0 if len(self.possible_agents) == 2 else 1)
                            ),
                            calculate_height(screen_height, 4, 1, tile_size, -1),
                        ),
                    )
                # Players with odd id go below public cards
                else:
                    self.screen.blit(
                        card_img,
                        (
                            (
                                calculate_width(self, screen_width, i)
                                - calculate_offset(state["hand"], j, tile_size)
                                - tile_size
                                * (8 / 10)
                                * (1 - np.ceil((i - 1) / 2))
                                * (0 if len(self.possible_agents) == 2 else 1)
                            ),
                            calculate_height(screen_height, 4, 3, tile_size, 0),
                        ),
                    )

            # Load and blit text for player name
            font = get_font(os.path.join("font", "Minecraft.ttf"), 36)
            text = font.render("Player " + str(i + 1), True, white)
            textRect = text.get_rect()
            if i % 2 == 0:
                textRect.center = (
                    (
                        screen_width
                        / (np.ceil(len(self.possible_agents) / 2) + 1)
                        * np.ceil((i + 1) / 2)
                        - tile_size
                        * (8 / 10)
                        * (1 - np.ceil(i / 2))
                        * (0 if len(self.possible_agents) == 2 else 1)
                    ),
                    calculate_height(screen_height, 4, 1, tile_size, -(22 / 20)),
                )
            else:
                textRect.center = (
                    (
                        screen_width
                        / (np.ceil(len(self.possible_agents) / 2) + 1)
                        * np.ceil((i + 1) / 2)
                        - tile_size
                        * (8 / 10)
                        * (1 - np.ceil((i - 1) / 2))
                        * (0 if len(self.possible_agents) == 2 else 1)
                    ),
                    calculate_height(screen_height, 4, 3, tile_size, (23 / 20)),
                )
            self.screen.blit(text, textRect)

            # Load and blit number of poker chips for each player
            font = get_font(os.path.join("font", "Minecraft.ttf"), 24)
            text = font.render(str(state["my_chips"]), True, white)
            textRect = text.get_rect()

            # Calculate number of each chip
            total = state["my_chips"]
            height = 0
            for key in chips:
                num = total / chips[key]["value"]
                chips[key]["number"] = int(num)
                total %= chips[key]["value"]

                chip_img = get_image(os.path.join("img", chips[key]["img"]))
                chip_img = pygame.transform.scale(
                    chip_img, (int(tile_size / 2), int(tile_size * 16 / 45))
                )

                # Blit poker chip img
                for j in range(0, int(chips[key]["number"])):
                    if i % 2 == 0:
                        self.screen.blit(
                            chip_img,
                            (
                                (
                                    calculate_width(self, screen_width, i)
                                    + tile_size
                                    * (8 / 10)
                                    * (
                                        1
                                        if len(self.possible_agents) == 2
                                        else np.ceil(i / 2)
                                    )
                                ),
                                calculate_height(screen_height, 4, 1, tile_size, -1 / 2)
                                - ((j + height) * tile_size / 15),
                            ),
                        )
                    else:
                        self.screen.blit(
                            chip_img,
                            (
                                (
                                    calculate_width(self, screen_width, i)
                                    + tile_size
                                    * (8 / 10)
                                    * (
                                        1
                                        if len(self.possible_agents) == 2
                                        else np.ceil((i - 1) / 2)
                                    )
                                ),
                                calculate_height(screen_height, 4, 3, tile_size, 1 / 2)
                                - ((j + height) * tile_size / 15),
                            ),
                        )
                height += chips[key]["number"]

            # Blit text number
            if i % 2 == 0:
                textRect.center = (
                    (
                        calculate_width(self, screen_width, i)
                        + (tile_size * (5 / 20))
                        + tile_size
                        * (8 / 10)
                        * (1 if len(self.possible_agents) == 2 else np.ceil(i / 2))
                    ),
                    calculate_height(screen_height, 4, 1, tile_size, -1 / 2)
                    - ((height + 1) * tile_size / 15),
                )
            else:
                textRect.center = (
                    (
                        calculate_width(self, screen_width, i)
                        + (tile_size * (5 / 20))
                        + tile_size
                        * (8 / 10)
                        * (
                            1
                            if len(self.possible_agents) == 2
                            else np.ceil((i - 1) / 2)
                        )
                    ),
                    calculate_height(screen_height, 4, 3, tile_size, 1 / 2)
                    - ((height + 1) * tile_size / 15),
                )
            self.screen.blit(text, textRect)

        # Load and blit public cards
        for i, card in enumerate(state["public_cards"]):
            card_img = get_image(os.path.join("img", card + ".png"))
            card_img = pygame.transform.scale(
                card_img, (int(tile_size * (142 / 197)), int(tile_size))
            )
            if len(state["public_cards"]) <= 3:
                self.screen.blit(
                    card_img,
                    (
                        (
                            (
                                ((screen_width / 2) + (tile_size * 31 / 616))
                                - calculate_offset(state["public_cards"], i, tile_size)
                            ),
                            calculate_height(screen_height, 2, 1, tile_size, -(1 / 2)),
                        )
                    ),
                )
            else:
                if i <= 2:
                    self.screen.blit(
                        card_img,
                        (
                            (
                                (
                                    ((screen_width / 2) + (tile_size * 31 / 616))
                                    - calculate_offset(
                                        state["public_cards"][:3], i, tile_size
                                    )
                                ),
                                calculate_height(
                                    screen_height, 2, 1, tile_size, -21 / 20
                                ),
                            )
                        ),
                    )
                else:
                    self.screen.blit(
                        card_img,
                        (
                            (
                                (
                                    ((screen_width / 2) + (tile_size * 31 / 616))
                                    - calculate_offset(
                                        state["public_cards"][3:], i - 3, tile_size
                                    )
                                ),
                                calculate_height(
                                    screen_height, 2, 1, tile_size, 1 / 20
                                ),
                            )
                        ),
                    )

        if self.render_mode == "human":
            pygame.display.update()
            self.clock.tick(self.metadata["render_fps"])

        observation = np.array(pygame.surfarray.pixels3d(self.screen))

        return (
            np.transpose(observation, axes=(1, 0, 2))
            if self.render_mode == "rgb_array"
            else None
        )
