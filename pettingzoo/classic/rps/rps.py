# noqa: D212, D415
"""
# Rock Paper Scissors

```{figure} classic_rps.gif
:width: 140px
:name: rps
```

This environment is part of the <a href='..'>classic environments</a>. Please read that page first for general information.

| Import             | `from pettingzoo.classic import rps_v2` |
|--------------------|-----------------------------------------|
| Actions            | Discrete                                |
| Parallel API       | Yes                                     |
| Manual Control     | No                                      |
| Agents             | `agents= ['player_0', 'player_1']`      |
| Agents             | 2                                       |
| Action Shape       | Discrete(3)                             |
| Action Values      | Discrete(3)                             |
| Observation Shape  | Discrete(4)                             |
| Observation Values | Discrete(4)                             |


Rock, Paper, Scissors is a 2-player hand game where each player chooses either rock, paper or scissors and reveals their choices simultaneously. If both players make the same choice, then it is a draw. However, if their choices are different, the winner is determined as follows: rock beats
scissors, scissors beat paper, and paper beats rock.

The game can be expanded to have extra actions by adding new action pairs. Adding the new actions in pairs allows for a more balanced game. This means that the final game will have an odd number of actions and each action wins over exactly half of the other actions while being defeated by the
other half. The most common expansion of this game is [Rock, Paper, Scissors, Lizard, Spock](http://www.samkass.com/theories/RPSSL.html), in which only one extra action pair is added.

### Arguments

``` python
rps_v2.env(num_actions=3, max_cycles=15)
```

`num_actions`:  number of actions applicable in the game. The default value is 3 for the game of Rock, Paper, Scissors. This argument must be an integer greater than 3 and with odd parity. If the value given is 5, the game is expanded to Rock, Paper, Scissors, Lizard, Spock.

`max_cycles`:  after max_cycles steps all agents will return done.

### Observation Space

#### Rock, Paper, Scissors

If 3 actions are required, the game played is the standard Rock, Paper, Scissors. The observation is the last opponent action and its space is a scalar value with 4 possible values. Since both players reveal their choices at the same time, the observation is None until both players have acted.
Therefore, 3 represents no action taken yet. Rock is represented with 0, paper with 1 and scissors with 2.

| Value  |  Observation |
| :----: | :---------:  |
| 0      | Rock         |
| 1      | Paper        |
| 2      | Scissors     |
| 3      | None         |

#### Expanded Game

If the number of actions required in the game is greater than 3, the observation is still the last opponent action and its space is a scalar with 1 + n possible values, where n is the number of actions. The observation will as well be None until both players have acted and the largest possible
scalar value for the space, 1 + n, represents no action taken yet. The additional actions are encoded in increasing order starting from the 0 Rock action. If 5 actions are required the game is expanded to Rock, Paper, Scissors, Lizard, Spock. The following table shows an example of an observation
space with 7 possible actions.

| Value  |  Observation |
| :----: | :---------:  |
| 0      | Rock         |
| 1      | Paper        |
| 2      | Scissors     |
| 3      | Lizard       |
| 4      | Spock        |
| 5      | Action_6     |
| 6      | Action_7     |
| 7      | None         |

### Action Space

#### Rock, Paper, Scissors

The action space is a scalar value with 3 possible values. The values are encoded as follows: Rock is 0, paper is 1 and scissors is 2.

| Value  |  Action |
| :----: | :---------:  |
| 0      | Rock         |
| 1      | Paper        |
| 2      | Scissors     |

#### Expanded Game

The action space is a scalar value with n possible values, where n is the number of additional action pairs. The values for 7 possible actions are encoded as in the following table.

| Value  |  Action |
| :----: | :---------:  |
| 0      | Rock         |
| 1      | Paper        |
| 2      | Scissors     |
| 3      | Lizard       |
| 4      | Spock        |
| 5      | Action_6     |
| 6      | Action_7     |

### Rewards

| Winner | Loser |
| :----: | :---: |
| +1     | -1    |

If the game ends in a draw, both players will receive a reward of 0.

### Version History

* v2: Merge RPS and rock paper lizard scissors spock environments, add num_actions and max_cycles arguments (1.9.0)
* v1: Bumped version of all environments due to adoption of new agent iteration scheme where all agents are iterated over after they are done (1.4.0)
* v0: Initial versions release (1.0.0)

"""
from __future__ import annotations

import os

import gymnasium
import numpy as np
import pygame
from gymnasium.spaces import Discrete
from gymnasium.utils import EzPickle

from pettingzoo import AECEnv
from pettingzoo.utils import agent_selector, wrappers
from pettingzoo.utils.conversions import parallel_wrapper_fn


def get_image(path):
    from os import path as os_path

    import pygame

    cwd = os_path.dirname(__file__)
    image = pygame.image.load(cwd + "/" + path)
    sfc = pygame.Surface(image.get_size(), flags=pygame.SRCALPHA)
    sfc.blit(image, (0, 0))
    return sfc


def get_font(path, size):
    from os import path as os_path

    cwd = os_path.dirname(__file__)
    font = pygame.font.Font((cwd + "/" + path), size)
    return font


def env(**kwargs):
    env = raw_env(**kwargs)
    env = wrappers.AssertOutOfBoundsWrapper(env)
    env = wrappers.OrderEnforcingWrapper(env)
    return env


parallel_env = parallel_wrapper_fn(env)


class raw_env(AECEnv, EzPickle):
    """Two-player environment for rock paper scissors.

    Expandable environment to rock paper scissors lizard spock action_6 action_7 ...
    The observation is simply the last opponent action.
    """

    metadata = {
        "render_modes": ["human", "rgb_array"],
        "name": "rps_v2",
        "is_parallelizable": True,
        "render_fps": 2,
    }

    def __init__(
        self,
        num_actions: int | None = 3,
        max_cycles: int | None = 15,
        render_mode: str | None = None,
        screen_height: int | None = 800,
    ):
        EzPickle.__init__(self, num_actions, max_cycles, render_mode, screen_height)
        super().__init__()
        self.max_cycles = max_cycles

        # number of actions must be odd and greater than 3
        assert num_actions > 2, "The number of actions must be equal or greater than 3."
        assert num_actions % 2 != 0, "The number of actions must be an odd number."
        self._moves = ["ROCK", "PAPER", "SCISSORS"]
        if num_actions > 3:
            # expand to lizard, spock for first extra action pair
            self._moves.extend(("SPOCK", "LIZARD"))
            for action in range(num_actions - 5):
                self._moves.append("ACTION_" f"{action + 6}")
        # none is last possible action, to satisfy discrete action space
        self._moves.append("None")
        self._none = num_actions

        self.agents = ["player_" + str(r) for r in range(2)]
        self.possible_agents = self.agents[:]
        self.agent_name_mapping = dict(zip(self.agents, list(range(self.num_agents))))
        self.action_spaces = {agent: Discrete(num_actions) for agent in self.agents}
        self.observation_spaces = {
            agent: Discrete(1 + num_actions) for agent in self.agents
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

    def render(self):
        if self.render_mode is None:
            gymnasium.logger.warn(
                "You are calling render method without specifying any render mode."
            )
            return

        def offset(i, size, offset=0):
            if i == 0:
                return -(size) - offset
            else:
                return offset

        screen_height = self.screen_height
        screen_width = int(screen_height * 5 / 14)

        # Load and all of the necessary images
        paper = get_image(os.path.join("img", "Paper.png"))
        rock = get_image(os.path.join("img", "Rock.png"))
        scissors = get_image(os.path.join("img", "Scissors.png"))
        spock = get_image(os.path.join("img", "Spock.png"))
        lizard = get_image(os.path.join("img", "Lizard.png"))

        # Scale images in history
        paper = pygame.transform.scale(
            paper, (int(screen_height / 9), int(screen_height / 9 * (14 / 12)))
        )
        rock = pygame.transform.scale(
            rock, (int(screen_height / 9), int(screen_height / 9 * (10 / 13)))
        )
        scissors = pygame.transform.scale(
            scissors, (int(screen_height / 9), int(screen_height / 9 * (14 / 13)))
        )
        spock = pygame.transform.scale(
            spock, (int(screen_height / 9), int(screen_height / 9))
        )
        lizard = pygame.transform.scale(
            lizard, (int(screen_height / 9 * (9 / 18)), int(screen_height / 9))
        )

        # Set background color
        bg = (255, 255, 255)
        self.screen.fill(bg)

        # Set font properties
        black = (0, 0, 0)
        font = get_font(
            (os.path.join("font", "Minecraft.ttf")), int(screen_height / 25)
        )

        for i, move in enumerate(self.history[0:10]):
            # Blit move history
            if self._moves[move] == "ROCK":
                self.screen.blit(
                    rock,
                    (
                        (screen_width / 2)
                        + offset((i) % 2, screen_height / 9, screen_height * 7 / 126),
                        (screen_height * 7 / 24)
                        + ((screen_height / 7) * np.floor(i / 2)),
                    ),
                )
            elif self._moves[move] == "PAPER":
                self.screen.blit(
                    paper,
                    (
                        (screen_width / 2)
                        + offset((i) % 2, screen_height / 9, screen_height * 7 / 126),
                        (screen_height * 7 / 24)
                        + ((screen_height / 7) * np.floor(i / 2)),
                    ),
                )
            elif self._moves[move] == "SCISSORS":
                self.screen.blit(
                    scissors,
                    (
                        (screen_width / 2)
                        + offset((i) % 2, screen_height / 9, screen_height * 7 / 126),
                        (screen_height * 7 / 24)
                        + ((screen_height / 7) * np.floor(i / 2)),
                    ),
                )
            elif self._moves[move] == "SPOCK":
                self.screen.blit(
                    spock,
                    (
                        (screen_width / 2)
                        + offset(
                            (i + 1) % 2, screen_height / 9, screen_height * 7 / 126
                        ),
                        (screen_height * 7 / 24)
                        + ((screen_height / 7) * np.floor(i / 2)),
                    ),
                )
            elif self._moves[move] == "LIZARD":
                self.screen.blit(
                    lizard,
                    (
                        (screen_width / 2)
                        + offset(
                            (i + 1) % 2, screen_height / 9, screen_height * 7 / 126
                        ),
                        (screen_height * 7 / 24)
                        + ((screen_height / 7) * np.floor(i / 2)),
                    ),
                )

        # Scale images in current game
        paper = pygame.transform.scale(
            paper, (int(screen_height / 7), int(screen_height / 7 * (14 / 12)))
        )
        rock = pygame.transform.scale(
            rock, (int(screen_height / 7), int(screen_height / 7 * (10 / 13)))
        )
        scissors = pygame.transform.scale(
            scissors, (int(screen_height / 7), int(screen_height / 7 * (14 / 13)))
        )
        spock = pygame.transform.scale(
            spock, (int(screen_height / 7), int(screen_height / 7))
        )
        lizard = pygame.transform.scale(
            lizard, (int(screen_height / 7 * (9 / 18)), int(screen_height / 7))
        )

        if len(self.agents) > 1:
            for i in range(0, 2):
                # Text for each agent
                text = font.render("Agent " + str(i + 1), True, black)
                textRect = text.get_rect()
                textRect.center = (
                    (screen_width / 2) + offset(i, 0, screen_width * 11 / 40),
                    screen_height / 40,
                )
                self.screen.blit(text, textRect)

                # Blit agent action
                if self._moves[self.state[self.agents[i]]] == "ROCK":
                    self.screen.blit(
                        rock,
                        (
                            (screen_width / 2)
                            + offset(i, screen_height / 7, screen_height / 42),
                            screen_height / 12,
                        ),
                    )
                elif self._moves[self.state[self.agents[i]]] == "PAPER":
                    self.screen.blit(
                        paper,
                        (
                            (screen_width / 2)
                            + offset(i, screen_height / 7, screen_height / 42),
                            screen_height / 12,
                        ),
                    )
                elif self._moves[self.state[self.agents[i]]] == "SCISSORS":
                    self.screen.blit(
                        scissors,
                        (
                            (screen_width / 2)
                            + offset(i, screen_height / 7, screen_height / 42),
                            screen_height / 12,
                        ),
                    )
                elif self._moves[self.state[self.agents[i]]] == "SPOCK":
                    self.screen.blit(
                        spock,
                        (
                            (screen_width / 2)
                            + offset(i, screen_height / 7, screen_height / 42),
                            screen_height / 12,
                        ),
                    )
                elif self._moves[self.state[self.agents[i]]] == "LIZARD":
                    self.screen.blit(
                        lizard,
                        (
                            (screen_width / 2)
                            + offset(i, screen_height / 7, screen_height / 42),
                            screen_height / 12,
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

    def observe(self, agent):
        # observation of one agent is the previous state of the other
        return np.array(self.observations[agent])

    def close(self):
        if self.screen is not None:
            pygame.quit()
            self.screen = None

    def reset(self, seed=None, options=None):
        self.agents = self.possible_agents[:]
        self._agent_selector = agent_selector(self.agents)
        self.agent_selection = self._agent_selector.next()
        self.rewards = {agent: 0 for agent in self.agents}
        self._cumulative_rewards = {agent: 0 for agent in self.agents}
        self.terminations = {agent: False for agent in self.agents}
        self.truncations = {agent: False for agent in self.agents}
        self.infos = {agent: {} for agent in self.agents}

        self.state = {agent: self._none for agent in self.agents}
        self.observations = {agent: self._none for agent in self.agents}

        self.history = [-1] * (2 * 5)

        self.num_moves = 0

        screen_height = self.screen_height
        screen_width = int(screen_height * 5 / 14)

        if self.screen is None:
            pygame.init()

        if self.render_mode == "human":
            self.screen = pygame.display.set_mode((screen_width, screen_height))
            pygame.display.set_caption("Rock Paper Scissors")
        else:
            self.screen = pygame.Surface((screen_width, screen_height))

    def step(self, action):
        if (
            self.terminations[self.agent_selection]
            or self.truncations[self.agent_selection]
        ):
            self._was_dead_step(action)
            return

        agent = self.agent_selection

        self.state[self.agent_selection] = action

        # collect reward if it is the last agent to act
        if self._agent_selector.is_last():
            # same action => 0 reward each agent
            if self.state[self.agents[0]] == self.state[self.agents[1]]:
                rewards = (0, 0)
            else:
                # same action parity => lower action number wins
                if (self.state[self.agents[0]] + self.state[self.agents[1]]) % 2 == 0:
                    if self.state[self.agents[0]] > self.state[self.agents[1]]:
                        rewards = (-1, 1)
                    else:
                        rewards = (1, -1)
                # different action parity => higher action number wins
                else:
                    if self.state[self.agents[0]] > self.state[self.agents[1]]:
                        rewards = (1, -1)
                    else:
                        rewards = (-1, 1)
            self.rewards[self.agents[0]], self.rewards[self.agents[1]] = rewards

            self.num_moves += 1

            self.truncations = {
                agent: self.num_moves >= self.max_cycles for agent in self.agents
            }
            for i in self.agents:
                self.observations[i] = self.state[
                    self.agents[1 - self.agent_name_mapping[i]]
                ]

            if self.render_mode == "human":
                self.render()

            # record history by pushing back
            self.history[2:] = self.history[:-2]
            self.history[0] = self.state[self.agents[0]]
            self.history[1] = self.state[self.agents[1]]

        else:
            self.state[self.agents[1 - self.agent_name_mapping[agent]]] = self._none

            self._clear_rewards()

            if self.render_mode == "human":
                self.render()

        self._cumulative_rewards[self.agent_selection] = 0
        self.agent_selection = self._agent_selector.next()
        self._accumulate_rewards()
