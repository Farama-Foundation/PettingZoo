# noqa: D212, D415
"""
# Texas Hold'em

```{figure} classic_texas_holdem.gif
:width: 140px
:name: texas_holdem
```

This environment is part of the <a href='..'>classic environments</a>. Please read that page first for general information.

| Creation           | `make("aec", "classic/texas_holdem-v5")`         |
|--------------------|--------------------------------------------------|
| Actions            | Discrete                                         |
| Parallel API       | No                                               |
| Manual Control     | No                                               |
| Agents             | `agents= ['player_0', 'player_1']`               |
| Agents             | 2                                                |
| Action Shape       | Discrete(3)                                      |
| Action Values      | Discrete(3)                                      |
| Observation Shape  | (108,)                                           |
| Observation Values | [0, 48]                                          |


## Arguments

```python
from pettingzoo import make

make("aec", "classic/texas_holdem-v5", num_players=2)
```

`num_players`: Sets the number of players in the game. The supported range is 2
to 4.

The game logic is provided by OpenSpiel's `universal_poker` implementation via
Shimmy. OpenSpiel requires Python 3.11 or newer.

### Observation Space

The observation is a dictionary which contains an `'observation'` element which is the usual RL observation described below, and an  `'action_mask'` which holds the legal moves, described in the Legal Actions Mask section.

The main observation is OpenSpiel's canonical poker observation tensor. Its
length is `104 + 2 * num_players`, or 108 for the default two-player game.
Cards use a 52-bit, rank-major encoding ordered as `2c, 2d, 2h, 2s, ...,
Ac, Ad, Ah, As`.

| Index | Description |
|:-----:|-------------|
| `0` to `n-1` | One-hot encoding of the observing player |
| `n` to `n+51` | The observing player's two private cards |
| `n+52` to `n+103` | The public community cards |
| `n+104` to `n+103+n` | Each player's total contribution to the pot |

#### Legal Actions Mask

The legal moves available to the current agent are found in the `action_mask` element of the dictionary observation. The `action_mask` is a binary vector where each index of the vector represents whether the action is legal or not. The `action_mask` will be all zeros for any agent except the one
whose turn it is. Taking an illegal move ends the game with a reward of -1 for the illegally moving agent and a reward of 0 for all other agents.

### Action Space

| Action ID | Action |
|:---------:|--------|
|     0     | Fold      |
|     1     | Check/Call |
|     2     | Bet/Raise  |

### Rewards

| Winner          | Loser           |
| :-------------: | :-------------: |
| +raised chips/2 | -raised chips/2 |

### Version History

* v5: Switched the backend from RLCard to OpenSpiel via Shimmy (1.28.0)
* v4: Upgrade to RLCard 1.0.3 (1.11.0)
* v3: Fixed bug in arbitrary calls to observe() (1.8.0)
* v2: Bumped RLCard version, bug fixes, legal action mask in observation replaced illegal move list in infos (1.5.0)
* v1: Bumped RLCard version, fixed observation space, adopted new agent iteration scheme where all agents are iterated over after they are done (1.4.0)
* v0: Initial versions release (1.0.0)

"""

from __future__ import annotations

import json
import os

import gymnasium
import numpy as np
import pygame
from gymnasium import spaces
from gymnasium.utils import EzPickle, seeding

from pettingzoo import AECEnv
from pettingzoo.classic.rlcard_envs.rlcard_utils import (
    calculate_height,
    calculate_offset,
    calculate_width,
    get_font,
    get_image,
)
from pettingzoo.utils import wrappers

# Pixel art from Mariia Khmelnytska (https://www.123rf.com/photo_104453049_stock-vector-pixel-art-playing-cards-standart-deck-vector-set.html)


def env(**kwargs):
    env = raw_env(**kwargs)
    env = wrappers.TerminateIllegalWrapper(env, illegal_reward=-1)
    env = wrappers.AssertOutOfBoundsWrapper(env)
    env = wrappers.OrderEnforcingWrapper(env)
    return env


class raw_env(AECEnv, EzPickle):
    metadata = {
        "render_modes": ["human", "rgb_array"],
        "name": "texas_holdem_v5",
        "is_parallelizable": False,
        "render_fps": 1,
    }

    game_name = "universal_poker"
    reward_scale = 0.5

    def __init__(
        self,
        num_players: int = 2,
        render_mode: str | None = None,
        screen_height: int | None = 1000,
    ):
        EzPickle.__init__(self, num_players, render_mode, screen_height)
        AECEnv.__init__(self)

        if not 2 <= num_players <= 4:
            raise ValueError(
                "Texas Hold'em supports between 2 and 4 players when using "
                "OpenSpiel's universal_poker backend."
            )

        try:
            from shimmy.openspiel_compatibility import OpenSpielCompatibilityV0
        except ImportError as e:
            raise ImportError(
                "Texas Hold'em depends on OpenSpiel via Shimmy, which requires "
                "Python >= 3.11. Install it with: pip install open_spiel"
            ) from e

        self.num_players = num_players
        self.np_random, self.np_random_seed = seeding.np_random(None)
        self._config = self._game_config(small_blind=0)
        self.texas_holdem_env = OpenSpielCompatibilityV0(
            game_name=self.game_name, render_mode=None, config=self._config
        )
        self.possible_agents = self.texas_holdem_env.possible_agents
        self.action_spaces = {
            agent: self.texas_holdem_env.action_space(agent)
            for agent in self.possible_agents
        }
        self.observation_spaces = {
            agent: spaces.Dict(
                {
                    "observation": self.texas_holdem_env.observation_space(agent),
                    "action_mask": spaces.Box(
                        low=0,
                        high=1,
                        shape=(self.texas_holdem_env.action_space(agent).n,),
                        dtype=np.int8,
                    ),
                }
            )
            for agent in self.possible_agents
        }

        assert render_mode is None or render_mode in self.metadata["render_modes"], (
            f"{render_mode} is not a valid render mode. Available modes are: "
            f"{self.metadata['render_modes']}"
        )
        self.render_mode = render_mode
        self.screen_height = screen_height
        self.caption = "Texas Hold'em"
        self.screen = None

        if self.render_mode == "human":
            self.clock = pygame.time.Clock()

    def _game_config(self, small_blind: int) -> dict:
        """Build a standard fixed-limit Texas Hold'em OpenSpiel configuration."""
        big_blind = (small_blind + 1) % self.num_players
        preflop_first = (big_blind + 1) % self.num_players
        postflop_first = big_blind if self.num_players == 2 else small_blind

        blinds = [0] * self.num_players
        blinds[small_blind] = 1
        blinds[big_blind] = 2

        return {
            "betting": "limit",
            "bettingAbstraction": "fcpa",
            "numPlayers": self.num_players,
            "numRounds": 4,
            "blind": " ".join(str(blind) for blind in blinds),
            # Although ignored for limit poker, OpenSpiel's ACPC parser expects
            # one stack entry per player for some player counts.
            "stack": " ".join("1200" for _ in range(self.num_players)),
            "raiseSize": "2 2 4 4",
            "firstPlayer": (
                f"{preflop_first + 1} "
                f"{postflop_first + 1} "
                f"{postflop_first + 1} "
                f"{postflop_first + 1}"
            ),
            # Match OpenSpiel's canonical HULH definition. The big blind
            # occupies the first pre-flop bet, leaving three raises there.
            "maxRaises": "3 4 4 4",
            "numSuits": 4,
            "numRanks": 13,
            "numHoleCards": 2,
            "numBoardCards": "0 3 1 1",
        }

    def observation_space(self, agent):
        return self.observation_spaces[agent]

    def action_space(self, agent):
        return self.action_spaces[agent]

    def observe(self, agent):
        observation = self.texas_holdem_env.observe(agent)
        action_mask = self.infos.get(agent, {}).get("action_mask")
        if action_mask is None:
            action_mask = np.zeros(self.action_space(agent).n, dtype=np.int8)
        return {"observation": observation, "action_mask": action_mask}

    def reset(self, seed=None, options=None):
        if seed is not None:
            self.np_random, self.np_random_seed = seeding.np_random(seed)

        small_blind = int(self.np_random.integers(self.num_players))
        openspiel_seed = int(self.np_random.integers(np.iinfo(np.int32).max))
        self._config = self._game_config(small_blind)
        self.texas_holdem_env.config = self._config
        self.texas_holdem_env.reset(seed=openspiel_seed)

        self.agents = self.possible_agents[:]
        self.agent_selection = self.texas_holdem_env.agent_selection
        self.rewards = dict.fromkeys(self.agents, 0.0)
        self._cumulative_rewards = dict.fromkeys(self.agents, 0.0)
        self.terminations = dict(self.texas_holdem_env.terminations)
        self.truncations = dict(self.texas_holdem_env.truncations)
        self.infos = dict(self.texas_holdem_env.infos)

    def step(self, action):
        if (
            self.terminations[self.agent_selection]
            or self.truncations[self.agent_selection]
        ):
            return self._was_dead_step(action)

        acting_agent = self.agent_selection
        self._cumulative_rewards[acting_agent] = 0
        self.texas_holdem_env.step(action)

        self.agent_selection = self.texas_holdem_env.agent_selection
        self.rewards = {
            agent: self.texas_holdem_env.rewards[agent] * self.reward_scale
            for agent in self.agents
        }
        self.terminations = {
            agent: self.texas_holdem_env.terminations[agent] for agent in self.agents
        }
        self.truncations = {
            agent: self.texas_holdem_env.truncations[agent] for agent in self.agents
        }
        self.infos = {
            agent: self.texas_holdem_env.infos[agent] for agent in self.agents
        }
        self._accumulate_rewards()

        if self.render_mode == "human":
            self.render()

    @staticmethod
    def _parse_openspiel_cards(cards: str) -> list[str]:
        """Convert concatenated OpenSpiel cards (Qc7h) to image names (CQ, H7)."""
        return [
            f"{cards[index + 1].upper()}{cards[index].upper()}"
            for index in range(0, len(cards), 2)
        ]

    def render(self):
        if self.render_mode is None:
            gymnasium.logger.warn(
                "You are calling render method without specifying any render mode."
            )
            return None

        if not hasattr(self.texas_holdem_env, "game_state"):
            gymnasium.logger.warn(
                "You are calling render method before reset() has been called."
            )
            return None

        game_state = json.loads(self.texas_holdem_env.game_state.to_json())
        player_hands = [
            self._parse_openspiel_cards(hand) for hand in game_state["player_hands"]
        ]
        public_cards = self._parse_openspiel_cards(game_state["board_cards"])
        player_contributions = game_state["player_contributions"]

        screen_height = self.screen_height
        screen_width = int(
            screen_height * (1 / 20)
            + np.ceil(len(self.possible_agents) / 2) * (screen_height * 12 / 20)
        )

        if self.screen is None:
            pygame.font.init()

            if self.render_mode == "human":
                pygame.display.init()
                self.screen = pygame.display.set_mode((screen_width, screen_height))
                pygame.display.set_caption(self.caption)
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
        for i, _player in enumerate(self.possible_agents):
            hand = player_hands[i]
            for j, card in enumerate(hand):
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
                                calculate_width(
                                    self.possible_agents,
                                    screen_width,
                                    i,
                                    tile_size,
                                    tile_scale=33,
                                )
                                - calculate_offset(hand, j, tile_size)
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
                                calculate_width(
                                    self.possible_agents,
                                    screen_width,
                                    i,
                                    tile_size,
                                    tile_scale=33,
                                )
                                - calculate_offset(hand, j, tile_size)
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
            text = font.render(str(player_contributions[i]), True, white)
            textRect = text.get_rect()

            # Calculate number of each chip
            total = player_contributions[i]
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
                for j in range(int(chips[key]["number"])):
                    if i % 2 == 0:
                        self.screen.blit(
                            chip_img,
                            (
                                (
                                    calculate_width(
                                        self.possible_agents,
                                        screen_width,
                                        i,
                                        tile_size,
                                        tile_scale=33,
                                    )
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
                                    calculate_width(
                                        self.possible_agents,
                                        screen_width,
                                        i,
                                        tile_size,
                                        tile_scale=33,
                                    )
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
                        calculate_width(
                            self.possible_agents,
                            screen_width,
                            i,
                            tile_size,
                            tile_scale=33,
                        )
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
                        calculate_width(
                            self.possible_agents,
                            screen_width,
                            i,
                            tile_size,
                            tile_scale=33,
                        )
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
        for i, card in enumerate(public_cards):
            card_img = get_image(os.path.join("img", card + ".png"))
            card_img = pygame.transform.scale(
                card_img, (int(tile_size * (142 / 197)), int(tile_size))
            )
            if len(public_cards) <= 3:
                self.screen.blit(
                    card_img,
                    (
                        (
                            (
                                ((screen_width / 2) + (tile_size * 31 / 616))
                                - calculate_offset(public_cards, i, tile_size)
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
                                    - calculate_offset(public_cards[:3], i, tile_size)
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
                                        public_cards[3:], i - 3, tile_size
                                    )
                                ),
                                calculate_height(
                                    screen_height, 2, 1, tile_size, 1 / 20
                                ),
                            )
                        ),
                    )

        if self.render_mode == "human":
            pygame.event.pump()
            pygame.display.update()
            self.clock.tick(self.metadata["render_fps"])

        observation = np.array(pygame.surfarray.pixels3d(self.screen))

        return (
            np.transpose(observation, axes=(1, 0, 2))
            if self.render_mode == "rgb_array"
            else None
        )

    def close(self):
        if self.screen is not None:
            pygame.display.quit()
            pygame.quit()
            self.screen = None
