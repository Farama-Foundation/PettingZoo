import os

import numpy as np
import pygame
from gym.spaces import Discrete

from pettingzoo import AECEnv
from pettingzoo.utils import agent_selector, wrappers
from pettingzoo.utils.conversions import parallel_wrapper_fn


def get_image(path):
    from os import path as os_path

    import pygame
    cwd = os_path.dirname(__file__)
    image = pygame.image.load(cwd + '/' + path)
    sfc = pygame.Surface(image.get_size(), flags=pygame.SRCALPHA)
    sfc.blit(image, (0, 0))
    return sfc


def get_font(path, size):
    from os import path as os_path
    cwd = os_path.dirname(__file__)
    font = pygame.font.Font((cwd + '/' + path), size)
    return font


def env(**kwargs):
    env = raw_env(**kwargs)
    env = wrappers.AssertOutOfBoundsWrapper(env)
    env = wrappers.OrderEnforcingWrapper(env)
    return env


parallel_env = parallel_wrapper_fn(env)


class raw_env(AECEnv):
    """Two-player environment for rock paper scissors.
    Expandable environment to rock paper scissors lizard spock action_6 action_7 ...
    The observation is simply the last opponent action."""

    metadata = {
        "render.modes": ["human", "rgb_array"],
        "name": "rps_v2",
        "is_parallelizable": True,
        "video.frames_per_second": 2,
    }

    def __init__(self, num_actions=3, max_cycles=15):
        self.max_cycles = max_cycles

        # number of actions must be odd and greater than 3
        assert num_actions > 2, "The number of actions must be equal or greater than 3."
        assert num_actions % 2 != 0, "The number of actions must be an odd number."
        self._moves = ["ROCK", "PAPER", "SCISSORS"]
        if num_actions > 3:
            # expand to lizard, spock for first extra action pair
            self._moves.extend(("SPOCK", "LIZARD"))
            for action in range(num_actions - 5):
                self._moves.append("ACTION_"f'{action + 6}')
        # none is last possible action, to satisfy discrete action space
        self._moves.append("None")
        self._none = num_actions

        self.agents = ["player_" + str(r) for r in range(2)]
        self.possible_agents = self.agents[:]
        self.agent_name_mapping = dict(zip(self.agents, list(range(self.num_agents))))
        self.action_spaces = {agent: Discrete(num_actions) for agent in self.agents}
        self.observation_spaces = {agent: Discrete(1 + num_actions) for agent in self.agents}

        self.screen = None
        self.history = [0] * (2 * 5)

        self.reinit()

    def observation_space(self, agent):
        return self.observation_spaces[agent]

    def action_space(self, agent):
        return self.action_spaces[agent]

    def reinit(self):
        self.agents = self.possible_agents[:]
        self._agent_selector = agent_selector(self.agents)
        self.agent_selection = self._agent_selector.next()
        self.rewards = {agent: 0 for agent in self.agents}
        self._cumulative_rewards = {agent: 0 for agent in self.agents}
        self.dones = {agent: False for agent in self.agents}
        self.infos = {agent: {} for agent in self.agents}

        self.state = {agent: self._none for agent in self.agents}
        self.observations = {agent: self._none for agent in self.agents}

        self.num_moves = 0

    def render(self, mode="human"):
        def offset(i, size, offset=0):
            if i == 0:
                return -(size) - offset
            else:
                return offset

        screen_height = 350
        screen_width = int(screen_height * 5 / 14)

        if self.screen is None:
            if mode == "human":
                pygame.init()
                self.screen = pygame.display.set_mode((screen_width, screen_height))
            else:
                pygame.font.init()
                self.screen = pygame.Surface((screen_width, screen_height))
        if mode == "human":
            pygame.event.get()

        # Load and all of the necessary images
        paper = get_image(os.path.join('img', 'Paper.png'))
        rock = get_image(os.path.join('img', 'Rock.png'))
        scissors = get_image(os.path.join('img', 'Scissors.png'))
        spock = get_image(os.path.join('img', 'Spock.png'))
        lizard = get_image(os.path.join('img', 'Lizard.png'))

        # Scale images in history
        paper = pygame.transform.scale(paper, (int(screen_height / 9), int(screen_height / 9 * (14 / 12))))
        rock = pygame.transform.scale(rock, (int(screen_height / 9), int(screen_height / 9 * (10 / 13))))
        scissors = pygame.transform.scale(scissors, (int(screen_height / 9), int(screen_height / 9 * (14 / 13))))
        spock = pygame.transform.scale(spock, (int(screen_height / 9), int(screen_height / 9)))
        lizard = pygame.transform.scale(lizard, (int(screen_height / 9 * (9 / 18)), int(screen_height / 9)))

        # Set background color
        bg = (255, 255, 255)
        self.screen.fill(bg)

        # Set font properties
        black = (0, 0, 0)
        font = get_font((os.path.join('font', 'Minecraft.ttf')), int(screen_height / 25))

        for i, move in enumerate(self.history[0:10]):
            # Blit move history
            if move == 'ROCK':
                self.screen.blit(rock, ((screen_width / 2) + offset((i + 1) % 2, screen_height / 9, screen_height * 7 / 126), (screen_height * 7 / 24) + ((screen_height / 7) * np.floor(i / 2))))
            elif move == 'PAPER':
                self.screen.blit(paper, ((screen_width / 2) + offset((i + 1) % 2, screen_height / 9, screen_height * 7 / 126), (screen_height * 7 / 24) + ((screen_height / 7) * np.floor(i / 2))))
            elif move == 'SCISSORS':
                self.screen.blit(scissors, ((screen_width / 2) + offset((i + 1) % 2, screen_height / 9, screen_height * 7 / 126), (screen_height * 7 / 24) + ((screen_height / 7) * np.floor(i / 2))))
            elif move == 'SPOCK':
                self.screen.blit(spock, ((screen_width / 2) + offset((i + 1) % 2, screen_height / 9, screen_height * 7 / 126), (screen_height * 7 / 24) + ((screen_height / 7) * np.floor(i / 2))))
            elif move == 'LIZARD':
                self.screen.blit(lizard, ((screen_width / 2) + offset((i + 1) % 2, screen_height / 9, screen_height * 7 / 126), (screen_height * 7 / 24) + ((screen_height / 7) * np.floor(i / 2))))

        # Scale images in current game
        paper = pygame.transform.scale(paper, (int(screen_height / 7), int(screen_height / 7 * (14 / 12))))
        rock = pygame.transform.scale(rock, (int(screen_height / 7), int(screen_height / 7 * (10 / 13))))
        scissors = pygame.transform.scale(scissors, (int(screen_height / 7), int(screen_height / 7 * (14 / 13))))
        spock = pygame.transform.scale(spock, (int(screen_height / 7), int(screen_height / 7)))
        lizard = pygame.transform.scale(lizard, (int(screen_height / 7 * (9 / 18)), int(screen_height / 7)))

        if len(self.agents) > 1:
            for i in range(0, 2):
                # Text for each agent
                text = font.render('Agent ' + str(i + 1), True, black)
                textRect = text.get_rect()
                textRect.center = ((screen_width / 2) + offset(i, 0, screen_width * 11 / 40), screen_height / 40)
                self.screen.blit(text, textRect)

                # Blit agent action
                if self._moves[self.state[self.agents[i]]] == 'ROCK':
                    self.screen.blit(rock, ((screen_width / 2) + offset(i, screen_height / 7, screen_height / 42), screen_height / 12))
                elif self._moves[self.state[self.agents[i]]] == 'PAPER':
                    self.screen.blit(paper, ((screen_width / 2) + offset(i, screen_height / 7, screen_height / 42), screen_height / 12))
                elif self._moves[self.state[self.agents[i]]] == 'SCISSORS':
                    self.screen.blit(scissors, ((screen_width / 2) + offset(i, screen_height / 7, screen_height / 42), screen_height / 12))
                elif self._moves[self.state[self.agents[i]]] == 'SPOCK':
                    self.screen.blit(spock, ((screen_width / 2) + offset(i, screen_height / 7, screen_height / 42), screen_height / 12))
                elif self._moves[self.state[self.agents[i]]] == 'LIZARD':
                    self.screen.blit(lizard, ((screen_width / 2) + offset(i, screen_height / 7, screen_height / 42), screen_height / 12))
                if self._moves[self.state[self.agents[1]]] != 'None':
                    self.history = [self._moves[self.state[self.agents[i]]]] + self.history[:-1]

        if mode == "human":
            pygame.display.update()

        observation = np.array(pygame.surfarray.pixels3d(self.screen))

        return np.transpose(observation, axes=(1, 0, 2)) if mode == "rgb_array" else None

    def observe(self, agent):
        # observation of one agent is the previous state of the other
        return np.array(self.observations[agent])

    def close(self):
        pass

    def reset(self):
        self.reinit()

    def step(self, action):
        if self.dones[self.agent_selection]:
            return self._was_done_step(action)
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

            self.dones = {agent: self.num_moves >= self.max_cycles for agent in self.agents}

            # observe the current state
            for i in self.agents:
                self.observations[i] = self.state[self.agents[1 - self.agent_name_mapping[i]]]
        else:
            self.state[self.agents[1 - self.agent_name_mapping[agent]]] = self._none

            self._clear_rewards()

        self._cumulative_rewards[self.agent_selection] = 0
        self.agent_selection = self._agent_selector.next()
        self._accumulate_rewards()
