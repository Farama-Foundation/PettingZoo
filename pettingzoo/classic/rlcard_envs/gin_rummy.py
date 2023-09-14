# noqa: D212, D415
"""
# Gin Rummy

```{figure} classic_gin_rummy.gif
:width: 140px
:name: gin_rummy
```

This environment is part of the <a href='..'>classic environments</a>. Please read that page first for general information.

| Import             | `from pettingzoo.classic import gin_rummy_v4` |
|--------------------|-----------------------------------------------|
| Actions            | Discrete                                      |
| Parallel API       | Yes                                           |
| Manual Control     | No                                            |
| Agents             | `agents= ['player_0', 'player_1']`            |
| Agents             | 2                                             |
| Action Shape       | Discrete(110)                                 |
| Action Values      | Discrete(110)                                 |
| Observation Shape  | (5, 52)                                       |
| Observation Values | [0,1]                                         |


Gin Rummy is a 2-player card game with a 52 card deck. The objective is to combine 3 or more cards of the same rank or in a sequence of the same suit.

Our implementation wraps [RLCard](http://rlcard.org/games.html#gin-rummy) and you can refer to its documentation for additional details. Please cite their work if you use this game in research.

### Arguments

Gin Rummy takes two optional arguments that define the reward received by a player who knocks or goes gin. The default values for the knock reward and gin reward are 0.5 and 1.0, respectively.

``` python
gin_rummy_v4.env(knock_reward = 0.5, gin_reward = 1.0, opponents_hand_visible = False)
```

`knock_reward`:  reward received by a player who knocks

`gin_reward`:  reward received by a player who goes gin

`opponents_hand_visible`:  Set to `True` to observe the entire observation space as described in `Observation Space` below. Setting it to `False` will remove any observation of the unknown cards and the observation space will only include planes 0 to 3.

### Observation Space

The observation is a dictionary which contains an `'observation'` element which is the usual RL observation described below, and an  `'action_mask'` which holds the legal moves, described in the Legal Actions Mask section.

The main observation space is 5x52 with the rows representing different planes and columns representing the 52 cards in a deck. The cards are ordered by suit (spades, hearts, diamonds, then clubs) and within each suit are ordered by rank (from Ace to King).

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

#### Legal Actions Mask

The legal moves available to the current agent are found in the `action_mask` element of the dictionary observation. The `action_mask` is a binary vector where each index of the vector represents whether the action is legal or not. The `action_mask` will be all zeros for any agent except the one
whose turn it is. Taking an illegal move ends the game with a reward of -1 for the illegally moving agent and a reward of 0 for all other agents.

### Action Space

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

### Rewards

At the end of the game, a player who gins is awarded 1 point, a player who knocks is awarded 0.5 points, and the losing player receives a reward equal to the negative of their deadwood count.

If the hand is declared dead, both players get a reward equal to negative of their deadwood count.

| End Action                                | Winner | Loser                   |
| ----------------------------------------- | :----: | ----------------------- |
| Dead Hand<br>_Both players are penalized_ |   --   | `-deadwood_count / 100` |
| Knock<br>_Knocking player: Default +0.5_  |   --   | `-deadwood_count / 100` |
| Gin<br>_Going Gin Player: Default +1_     |   --   | `-deadwood_count / 100` |

Note that the defaults are slightly different from those in RLcard- their default reward for knocking is 0.2.

Penalties of `deadwood_count / 100` ensure that the reward never goes below -1.

### Version History

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
from gymnasium.utils import EzPickle
from rlcard.games.gin_rummy.player import GinRummyPlayer
from rlcard.games.gin_rummy.utils import melding as melding
from rlcard.games.gin_rummy.utils import utils
from rlcard.games.gin_rummy.utils.action_event import GinAction, KnockAction

from pettingzoo.classic.rlcard_envs.rlcard_base import RLCardBase
from pettingzoo.utils import wrappers


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
        "name": "gin_rummy_v4",
        "is_parallelizable": False,
        "render_fps": 1,
    }

    def __init__(
        self,
        knock_reward: float = 0.5,
        gin_reward: float = 1.0,
        opponents_hand_visible: bool | None = False,
        render_mode: str | None = None,
        screen_height: int | None = 1000,
    ):
        EzPickle.__init__(
            self,
            knock_reward=knock_reward,
            gin_reward=gin_reward,
            render_mode=render_mode,
        )
        self._opponents_hand_visible = opponents_hand_visible
        num_planes = 5 if self._opponents_hand_visible else 4
        RLCardBase.__init__(self, "gin-rummy", 2, (num_planes, 52))
        self._knock_reward = knock_reward
        self._gin_reward = gin_reward

        self.env.game.judge.scorer.get_payoff = self._get_payoff
        self.render_mode = render_mode
        self.screen_height = screen_height
        self.save_states = None  # Used for rendering when agents are terminated.

        if self.render_mode == "human":
            self.clock = pygame.time.Clock()

    def _get_payoff(self, player: GinRummyPlayer, game) -> float:
        going_out_action = game.round.going_out_action
        going_out_player_id = game.round.going_out_player_id
        if (
            going_out_player_id == player.player_id
            and type(going_out_action) is KnockAction
        ):
            payoff = self._knock_reward
        elif (
            going_out_player_id == player.player_id
            and type(going_out_action) is GinAction
        ):
            payoff = self._gin_reward
        else:
            hand = player.hand
            best_meld_clusters = melding.get_best_meld_clusters(hand=hand)
            best_meld_cluster = [] if not best_meld_clusters else best_meld_clusters[0]
            deadwood_count = utils.get_deadwood_count(hand, best_meld_cluster)
            payoff = -deadwood_count / 100
        return payoff

    def observe(self, agent):
        obs = self.env.get_state(self._name_to_int(agent))
        if self._opponents_hand_visible:
            observation = obs["obs"].astype(self._dtype)
        else:
            observation = obs["obs"][0:4, :].astype(self._dtype)

        legal_moves = self.next_legal_moves
        action_mask = np.zeros(110, "int8")
        for i in legal_moves:
            action_mask[i] = 1

        return {"observation": observation, "action_mask": action_mask}

    def step(self, action):
        super().step(action)

        if self.render_mode == "human":
            self.render()

    """
    To render:
    state: {'player_id', 'hand', 'top_discard'}
    """

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

        def draw_borders(x, y, width, height, bw, color):
            pygame.draw.line(
                self.screen, color, (x - bw // 2 + 1, y), (x + width + bw // 2, y), bw
            )
            pygame.draw.line(
                self.screen,
                color,
                (x - bw // 2 + 1, y + height),
                (x + width + bw // 2, y + height),
                bw,
            )
            pygame.draw.line(
                self.screen, color, (x, y - bw // 2 + 1), (x, y + height + bw // 2), bw
            )
            pygame.draw.line(
                self.screen,
                color,
                (x + width, y - bw // 2 + 1),
                (x + width, y + height + bw // 2),
                bw,
            )

        screen_height = self.screen_height
        screen_width = int(screen_height * (1 / 20) + 3.5 * (screen_height * 1 / 2))

        if self.screen is None:
            pygame.init()

            if self.render_mode == "human":
                self.screen = pygame.display.set_mode((screen_width, screen_height))
                pygame.display.set_caption("Gin Rummy")
            else:
                self.screen = pygame.Surface((screen_width, screen_height))

        # Setup dimensions for card size and setup for colors
        tile_size = screen_height * 2 / 10

        bg_color = (7, 99, 36)
        white = (255, 255, 255)
        self.screen.fill(bg_color)

        # Load and blit all images for each card in each player's hand
        for i, player in enumerate(self.possible_agents):
            state = self.env.game.get_state(self._name_to_int(player))

            # This is to mitigate the issue of a blank board render without cards as env returns an empty state on
            # agent termination. Used to store states for renders when agents are terminated
            if len(state) == 0:
                state = self.save_states
            else:
                self.save_states = state

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

            for j, card in enumerate(state["top_discard"]):
                card_img = get_image(os.path.join("img", card + ".png"))
                card_img = pygame.transform.scale(
                    card_img, (int(tile_size * (142 / 197)), int(tile_size))
                )

                self.screen.blit(
                    card_img,
                    (
                        (
                            (
                                ((screen_width / 2) + (tile_size * 31 / 616))
                                - calculate_offset(state["top_discard"], j, tile_size)
                            ),
                            calculate_height(screen_height, 2, 1, tile_size, -(1 / 2)),
                        )
                    ),
                )

            # Load and blit discarded cards
            font = get_font(os.path.join("font", "Minecraft.ttf"), 36)
            text = font.render("Top Discarded Card", True, white)
            textRect = text.get_rect()
            textRect.center = (
                (calculate_width(self, screen_width, 0)),
                calculate_height(screen_height, 2, 1, tile_size, (-2 / 3))
                + (tile_size * (13 / 200)),
            )
            self.screen.blit(text, textRect)

            draw_borders(
                x=int((screen_width / 2) + (tile_size * 31 / 616))
                - int(tile_size * 23 / 56)
                - 5,
                y=calculate_height(screen_height, 2, 1, tile_size, -(1 / 2)) - 6,
                width=int(tile_size) - int(tile_size * (9 / 40)),
                height=int(tile_size) + 10,
                bw=3,
                color="white",
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
