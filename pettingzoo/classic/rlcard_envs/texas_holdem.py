# noqa
"""
# Texas Hold'em

```{figure} classic_texas_holdem.gif
:width: 140px
:name: texas_holdem
```

This environment is part of the <a href='..'>classic environments</a>. Please read that page first for general information.

| Import             | `from pettingzoo.classic import texas_holdem_v4` |
|--------------------|--------------------------------------------------|
| Actions            | Discrete                                         |
| Parallel API       | Yes                                              |
| Manual Control     | No                                               |
| Agents             | `agents= ['player_0', 'player_1']`               |
| Agents             | 2                                                |
| Action Shape       | Discrete(4)                                      |
| Action Values      | Discrete(4)                                      |
| Observation Shape  | (72,)                                            |
| Observation Values | [0, 1]                                           |


## Arguments

``` python
texas_holdem_v4.env(num_players=2)
```

`num_players`: Sets the number of players in the game. Minimum is 2.

### Observation Space

The observation is a dictionary which contains an `'observation'` element which is the usual RL observation described below, and an  `'action_mask'` which holds the legal moves, described in the Legal Actions Mask section.

The main observation space is a vector of 72 boolean integers. The first 52 entries depict the current player's hand plus any community cards as follows

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

#### Legal Actions Mask

The legal moves available to the current agent are found in the `action_mask` element of the dictionary observation. The `action_mask` is a binary vector where each index of the vector represents whether the action is legal or not. The `action_mask` will be all zeros for any agent except the one
whose turn it is. Taking an illegal move ends the game with a reward of -1 for the illegally moving agent and a reward of 0 for all other agents.

### Action Space

| Action ID | Action |
|:---------:|--------|
|     0     | Call   |
|     1     | Raise  |
|     2     | Fold   |
|     3     | Check  |

### Rewards

| Winner          | Loser           |
| :-------------: | :-------------: |
| +raised chips/2 | -raised chips/2 |

### Version History

* v4: Upgrade to RLCard 1.0.3 (1.11.0)
* v3: Fixed bug in arbitrary calls to observe() (1.8.0)
* v2: Bumped RLCard version, bug fixes, legal action mask in observation replaced illegal move list in infos (1.5.0)
* v1: Bumped RLCard version, fixed observation space, adopted new agent iteration scheme where all agents are iterated over after they are done (1.4.0)
* v0: Initial versions release (1.0.0)

"""

import os

import gymnasium
import numpy as np
import pygame

from pettingzoo.utils import wrappers

from .rlcard_base import RLCardBase

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


class raw_env(RLCardBase):

    metadata = {
        "render_modes": ["human", "rgb_array"],
        "name": "texas_holdem_v4",
        "is_parallelizable": False,
        "render_fps": 1,
    }

    def __init__(self, num_players=2, render_mode=None):
        super().__init__("limit-holdem", num_players, (72,))
        self.render_mode = render_mode

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
                + (tile_size * 31 / 616)
            )

        def calculate_offset(hand, j, tile_size):
            return int(
                (len(hand) * (tile_size * 23 / 56)) - ((j) * (tile_size * 23 / 28))
            )

        def calculate_height(screen_height, divisor, multiplier, tile_size, offset):
            return int(multiplier * screen_height / divisor + tile_size * offset)

        screen_height = 1000
        screen_width = int(
            screen_height * (1 / 20)
            + np.ceil(len(self.possible_agents) / 2) * (screen_height * 1 / 2)
        )

        if self.render_mode == "human":
            if self.screen is None:
                pygame.init()
                self.screen = pygame.display.set_mode((screen_width, screen_height))
            pygame.event.get()
        elif self.screen is None:
            pygame.font.init()
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
                    ),
                    calculate_height(screen_height, 4, 1, tile_size, -(22 / 20)),
                )
            else:
                textRect.center = (
                    (
                        screen_width
                        / (np.ceil(len(self.possible_agents) / 2) + 1)
                        * np.ceil((i + 1) / 2)
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
                                    + tile_size * (8 / 10)
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
                                    + tile_size * (8 / 10)
                                ),
                                calculate_height(screen_height, 4, 3, tile_size, 1 / 2)
                                - ((j + height) * tile_size / 15),
                            ),
                        )
                height += chips[key]["number"]

            # Blit text number
            if i % 2 == 0:
                textRect.center = (
                    (calculate_width(self, screen_width, i) + tile_size * (21 / 20)),
                    calculate_height(screen_height, 4, 1, tile_size, -1 / 2)
                    - ((height + 1) * tile_size / 15),
                )
            else:
                textRect.center = (
                    (calculate_width(self, screen_width, i) + tile_size * (21 / 20)),
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

        observation = np.array(pygame.surfarray.pixels3d(self.screen))

        return (
            np.transpose(observation, axes=(1, 0, 2))
            if self.render_mode == "rgb_array"
            else None
        )
