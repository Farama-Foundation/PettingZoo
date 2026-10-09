"""Leduc Hold'em using OpenSpiel's Leduc Poker implementation.

```{figure} classic_leduc_holdem.gif
:width: 140px
:name: leduc_holdem
```

This environment is part of the <a href='..'>classic environments</a>. Please read that page first for general information.

| Creation           | `make("aec", "classic/leduc_holdem-v5")` |
|--------------------|-------------------------------------------|
| Actions            | Discrete                                 |
| Parallel API       | No                                       |
| Manual Control     | No                                       |
| Agents             | `player_0`, `player_1`                   |
| Number of Agents   | 2                                        |
| Action Shape       | Discrete(3)                              |
| Action Values      | Discrete(3)                              |
| Observation Shape  | (16,)                                    |
| Observation Values | OpenSpiel observation tensor             |

Leduc Hold'em is a two-player, two-round poker game. Each player receives one
private card, then a public card is revealed between rounds. OpenSpiel provides
the game logic; both players ante one chip, and the first player is selected
randomly on each reset. OpenSpiel's observation tensor contains the observing player's
identity, private card, public card, and player contributions. It does not
include the other player's private card.

The observation is returned in a dictionary with an `observation` vector and an
`action_mask` vector. OpenSpiel uses three actions: `0` fold, `1` call or check,
and `2` raise. The action mask disables folding when there is no wager to call
and disables raising when the round's raise limit has been reached.

### Rewards

Terminal chip payoffs are divided by two, matching the reward scale documented
for earlier versions of this environment.

### Version History

* v5: Replaced the RLCard backend with OpenSpiel (1.28.0)
"""

from __future__ import annotations

import os

import gymnasium
import numpy as np
import pygame
from gymnasium import spaces
from gymnasium.utils import EzPickle, seeding

from pettingzoo import AECEnv
from pettingzoo.classic.rlcard_envs.rlcard_utils import get_font, get_image
from pettingzoo.utils import wrappers


def env(**kwargs):
    env = raw_env(**kwargs)
    env = wrappers.TerminateIllegalWrapper(env, illegal_reward=-1)
    env = wrappers.AssertOutOfBoundsWrapper(env)
    env = wrappers.OrderEnforcingWrapper(env)
    return env


class raw_env(AECEnv, EzPickle):
    """AEC wrapper around OpenSpiel's two-player Leduc Poker game."""

    metadata = {
        "render_modes": ["human", "rgb_array"],
        "name": "leduc_holdem_v5",
        "is_parallelizable": False,
        "render_fps": 1,
    }

    def __init__(
        self,
        render_mode: str | None = None,
        screen_height: int = 1000,
    ):
        EzPickle.__init__(self, render_mode, screen_height)
        AECEnv.__init__(self)

        try:
            from shimmy.openspiel_compatibility import OpenSpielCompatibilityV0
        except ImportError as e:
            raise ImportError(
                "Leduc Hold'em depends on OpenSpiel via Shimmy, which requires "
                "Python >= 3.11. Install it with: pip install open_spiel"
            ) from e

        if render_mode is not None and render_mode not in self.metadata["render_modes"]:
            raise ValueError(
                f"{render_mode} is not a valid render mode. Available modes are: "
                f"{self.metadata['render_modes']}"
            )

        self._config = {"players": 2, "action_mapping": False}
        self._rng, self._seed = seeding.np_random(None)
        self._rewards_scaled = False
        self.leduc_env = OpenSpielCompatibilityV0(
            game_name="leduc_poker", render_mode=None, config=self._config.copy()
        )
        self.possible_agents = self.leduc_env.possible_agents
        self.action_spaces = {
            agent: self.leduc_env.action_space(agent) for agent in self.possible_agents
        }
        self.observation_spaces = {
            agent: spaces.Dict(
                {
                    "observation": self.leduc_env.observation_space(agent),
                    "action_mask": spaces.Box(
                        low=0,
                        high=1,
                        shape=(self.leduc_env.action_space(agent).n,),
                        dtype=np.int8,
                    ),
                }
            )
            for agent in self.possible_agents
        }
        self.render_mode = render_mode
        self.screen_height = screen_height
        self.screen = None
        if self.render_mode == "human":
            self.clock = pygame.time.Clock()

    def observation_space(self, agent):
        return self.observation_spaces[agent]

    def action_space(self, agent):
        return self.action_spaces[agent]

    def observe(self, agent):
        return {
            "observation": self.leduc_env.observe(agent),
            "action_mask": self.leduc_env.infos[agent]["action_mask"],
        }

    def _sync_state(self):
        self.agents = self.leduc_env.agents
        self.agent_selection = self.leduc_env.agent_selection
        self.rewards = self.leduc_env.rewards
        self._cumulative_rewards = self.leduc_env._cumulative_rewards
        self.terminations = self.leduc_env.terminations
        self.truncations = self.leduc_env.truncations
        self.infos = self.leduc_env.infos

    def reset(self, seed=None, options=None):
        self._rng, self._seed = seeding.np_random(seed)
        self._config["starting_player"] = int(self._rng.integers(2))
        self.leduc_env.config = self._config.copy()
        self.leduc_env.reset(seed=seed, options=options)
        self._rewards_scaled = False
        self._sync_state()

    def step(self, action):
        self.leduc_env.step(action)

        # Shimmy truncates games after OpenSpiel's max_game_length(). For
        # Leduc, that value is shorter than valid two-round play paths, so
        # ignore the adapter's length truncation until OpenSpiel is terminal.
        if any(self.leduc_env.truncations.values()):
            self.leduc_env.truncations = dict.fromkeys(self.leduc_env.agents, False)
            if not self.leduc_env.game_state.is_terminal():
                player = self.leduc_env.game_state.current_player()
                self.leduc_env.agent_selection = self.leduc_env.agent_id_name_mapping[
                    player
                ]

        if any(self.leduc_env.terminations.values()) and not self._rewards_scaled:
            for agent in self.leduc_env.agents:
                self.leduc_env.rewards[agent] *= 0.5
                self.leduc_env._cumulative_rewards[agent] *= 0.5
            self._rewards_scaled = True

        self._sync_state()
        if self.render_mode is not None and not any(self.terminations.values()):
            self.render()

    @staticmethod
    def _card_image_name(card: int) -> str:
        """Map OpenSpiel's paired rank IDs to the existing card image names."""
        ranks = ("J", "Q", "K")
        suits = ("H", "D")
        return f"{suits[card % 2]}{ranks[card // 2]}"

    def render(self):
        if self.render_mode is None:
            gymnasium.logger.warn(
                "You are calling render method without specifying any render mode."
            )
            return None

        if not hasattr(self.leduc_env, "game_state"):
            gymnasium.logger.warn(
                "You are calling render method before reset() has been called."
            )
            return None

        screen_height = self.screen_height
        screen_width = int(screen_height * 0.55)
        tile_size = int(screen_height * 0.2)
        card_width = int(tile_size * (142 / 197))
        white = (255, 255, 255)

        if self.screen is None:
            pygame.font.init()
            if self.render_mode == "human":
                pygame.display.init()
                pygame.display.set_caption("Leduc Hold'em")
                self.screen = pygame.display.set_mode((screen_width, screen_height))
            else:
                self.screen = pygame.Surface((screen_width, screen_height))

        self.screen.fill((7, 99, 36))
        game_state = self.leduc_env.game_state

        for player in range(2):
            card = game_state.private_card(player)
            if card < 0:
                continue
            card_image = get_image(
                os.path.join("img", self._card_image_name(card) + ".png")
            )
            card_image = pygame.transform.scale(card_image, (card_width, tile_size))
            y = int(screen_height * (0.18 if player == 0 else 0.65))
            x = (screen_width - card_width) // 2
            self.screen.blit(card_image, (x, y))

            font = get_font(os.path.join("font", "Minecraft.ttf"), 28)
            label = font.render(f"Player {player + 1}", True, white)
            self.screen.blit(label, label.get_rect(center=(screen_width // 2, y - 24)))

            chips_font = get_font(os.path.join("font", "Minecraft.ttf"), 22)
            chips = chips_font.render(
                f"{int(game_state.money()[player])} chips", True, white
            )
            chips_y = y + tile_size + 26
            self.screen.blit(chips, chips.get_rect(center=(screen_width // 2, chips_y)))

        public_card = game_state.public_card()
        if public_card >= 0:
            card_image = get_image(
                os.path.join("img", self._card_image_name(public_card) + ".png")
            )
            card_image = pygame.transform.scale(card_image, (card_width, tile_size))
            x = (screen_width - card_width) // 2
            y = (screen_height - tile_size) // 2
            self.screen.blit(card_image, (x, y))

        if self.render_mode == "human":
            pygame.event.pump()
            pygame.display.update()
            self.clock.tick(self.metadata["render_fps"])
            return None

        return np.transpose(
            np.array(pygame.surfarray.pixels3d(self.screen)), axes=(1, 0, 2)
        )

    def close(self):
        if self.screen is not None:
            pygame.display.quit()
            self.screen = None
