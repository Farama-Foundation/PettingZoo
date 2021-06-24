from pettingzoo import AECEnv
from pettingzoo.utils.agent_selector import agent_selector
from gym import spaces
import rlcard
import random
import pygame
import os
from rlcard.utils.utils import print_card
import numpy as np
from pettingzoo.utils import wrappers
from .rlcard_base import RLCardBase


def get_image(path):
    from os import path as os_path
    cwd = os_path.dirname(__file__)
    image = pygame.image.load(cwd + '/' + path)
    return image


def get_font(path, size):
    from os import path as os_path
    cwd = os_path.dirname(__file__)
    font = pygame.font.Font((cwd + '/' + path), size)
    return font



def env(**kwargs):
    env = raw_env(**kwargs)
    env = wrappers.CaptureStdoutWrapper(env)
    env = wrappers.TerminateIllegalWrapper(env, illegal_reward=-1)
    env = wrappers.AssertOutOfBoundsWrapper(env)
    env = wrappers.OrderEnforcingWrapper(env)
    return env


class raw_env(RLCardBase):

    metadata = {'render.modes': ['human'], "name": "texas_holdem_no_limit_v3"}

    def __init__(self):
        super().__init__("no-limit-holdem", 2, (54,))
        self.observation_spaces = self._convert_to_dict([spaces.Dict(
            {'observation': spaces.Box(low=np.zeros(54, ), high=np.append(np.ones(52, ), [100, 100]), dtype=np.int8),
             'action_mask': spaces.Box(low=0, high=1, shape=(6,), dtype=np.int8)}) for _ in range(self.num_agents)])

    def render(self, mode='human'):

        def calculate_width(self, screen_width, i):
            return int((((screen_width / ((np.ceil(len(self.possible_agents) / 2) + 1)) * np.ceil((i + 1) / 2)))))

        def calculate_offset(hand, j, tile_size):
            return int((len(hand) * (tile_size / 2)) - ((j) * tile_size))

        def calculate_height(screen_height, divisor, multiplier, tile_size, offset):
            return int(multiplier * screen_height / divisor + tile_size * offset)

        screen_height = 1000
        screen_width = int(screen_height + np.ceil(len(self.possible_agents) / 2) * (screen_height / 5))

        if self.screen is None:
            if mode == "human":
                pygame.init()
                self.screen = pygame.display.set_mode((screen_width, screen_height))
            else:
                pygame.font.init()
                self.screen = pygame.Surface((screen_width, screen_height))
        if mode == "human":
            pygame.event.get()

        # Setup dimensions for card size and setup for colors
        tile_size = screen_height * 1.6 / 10

        bg_color = (7, 99, 36)
        white = (255, 255, 255)
        self.screen.fill(bg_color)

        # Load and blit all images for each card in each player's hand
        for i, player in enumerate(self.possible_agents):
            state = self.env.game.get_state(self._name_to_int(player))
            for j, card in enumerate(state['hand']):
                # Load specified card
                card_img = get_image(os.path.join('img', card + '.png'))
                card_img = pygame.transform.scale(card_img, (int(tile_size * (142 / 197)), int(tile_size)))
                # Players with even id go above public cards
                if i % 2 == 0:
                    self.screen.blit(card_img, ((calculate_width(self, screen_width, i) - calculate_offset(state['hand'], j, tile_size)), calculate_height(screen_height, 4, 1, tile_size, -1)))
                # Players with odd id go below public cards
                else:
                    self.screen.blit(card_img, ((calculate_width(self, screen_width, i) - calculate_offset(state['hand'], j, tile_size)), calculate_height(screen_height, 4, 3, tile_size, 0)))

            # Load and blit text for player name
            font = get_font(os.path.join('font', 'Minecraft.ttf'), 36)
            text = font.render("Player " + str(i + 1), True, white)
            textRect = text.get_rect()
            if i % 2 == 0:
                textRect.center = (calculate_width(self, screen_width, i), calculate_height(screen_height, 4, 1, tile_size, -(5 / 4)))
            else:
                textRect.center = (calculate_width(self, screen_width, i), calculate_height(screen_height, 4, 3, tile_size, -(1 / 4)))
            self.screen.blit(text, textRect)

            # Load and blit number of poker chips for each player
            font = get_font(os.path.join('font', 'Minecraft.ttf'), 24)
            text = font.render(str(state['my_chips']), True, white)
            textRect = text.get_rect()

            # Blit text number
            if i % 2 == 0:
                textRect.center = ((calculate_width(self, screen_width, i) + tile_size * (21 / 20)), calculate_height(screen_height, 4, 1, tile_size, 0) - ((state['my_chips'] + 1) * tile_size / 20))
            else:
                textRect.center = ((calculate_width(self, screen_width, i) + tile_size * (21 / 20)), calculate_height(screen_height, 4, 3, tile_size, 1) - ((state['my_chips'] + 1) * tile_size / 20))
            self.screen.blit(text, textRect)

            chip_img = get_image(os.path.join('img', 'PokerChip.png'))
            chip_img = pygame.transform.scale(chip_img, (int(tile_size / 2), int(tile_size * 5 / 16)))

            # Blit poker chip img
            for j in range(0, state['my_chips']):
                if i % 2 == 0:
                    self.screen.blit(chip_img, ((calculate_width(self, screen_width, i) + tile_size * (8 / 10)), calculate_height(screen_height, 4, 1, tile_size, 0) - (j * tile_size / 20)))
                else:
                    self.screen.blit(chip_img, ((calculate_width(self, screen_width, i) + tile_size * (8 / 10)), calculate_height(screen_height, 4, 3, tile_size, 1) - (j * tile_size / 20)))

        # Load and blit public cards
        for i, card in enumerate(state['public_cards']):
            card_img = get_image(os.path.join('img', card + '.png'))
            card_img = pygame.transform.scale(card_img, (int(tile_size * (142 / 197)), int(tile_size)))
            self.screen.blit(card_img, ((((screen_width / 2) - calculate_offset(state['public_cards'], i, tile_size)), calculate_height(screen_height, 2, 1, tile_size, -(1 / 2)))))

        if mode == "human":
            pygame.display.update()

        observation = np.array(pygame.surfarray.pixels3d(self.screen))

        return np.transpose(observation, axes=(1, 0, 2)) if mode == "rgb_array" else None
