import os
import random

import numpy as np
import pygame
import rlcard
from gym import spaces
from numpy.lib.shape_base import tile
from rlcard.utils.utils import print_card

from pettingzoo import AECEnv
from pettingzoo.utils import wrappers
from pettingzoo.utils.agent_selector import agent_selector

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
    env = wrappers.TerminateIllegalWrapper(env, illegal_reward=-1)
    env = wrappers.AssertOutOfBoundsWrapper(env)
    env = wrappers.OrderEnforcingWrapper(env)
    return env


class raw_env(RLCardBase):

    metadata = {
        "render.modes": ["human", "rgb_array"],
        "name": "texas_holdem_v4",
        "is_parallelizable": False,
        "video.frames_per_second": 1,
    }

    def __init__(self, num_players=2):
        super().__init__("limit-holdem", num_players, (72,))

    def render(self, mode='human'):

        def calculate_width(self, screen_width, i):
            return int((screen_width / (np.ceil(len(self.possible_agents) / 2) + 1) * np.ceil((i + 1) / 2)) + (tile_size * 31 / 616))

        def calculate_offset(hand, j, tile_size):
            return int((len(hand) * (tile_size * 23 / 56)) - ((j) * (tile_size * 23 / 28)))

        def calculate_height(screen_height, divisor, multiplier, tile_size, offset):
            return int(multiplier * screen_height / divisor + tile_size * offset)

        screen_height = 1000
        screen_width = int(screen_height * (1 / 20) + np.ceil(len(self.possible_agents) / 2) * (screen_height * 1 / 2))

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
        tile_size = screen_height * 2 / 10

        bg_color = (7, 99, 36)
        white = (255, 255, 255)
        self.screen.fill(bg_color)

        chips = {0: {'value': 10000, 'img': 'ChipOrange.png', 'number': 0},
                 1: {'value': 5000, 'img': 'ChipPink.png', 'number': 0},
                 2: {'value': 1000, 'img': 'ChipYellow.png', 'number': 0},
                 3: {'value': 100, 'img': 'ChipBlack.png', 'number': 0},
                 4: {'value': 50, 'img': 'ChipBlue.png', 'number': 0},
                 5: {'value': 25, 'img': 'ChipGreen.png', 'number': 0},
                 6: {'value': 10, 'img': 'ChipLightBlue.png', 'number': 0},
                 7: {'value': 5, 'img': 'ChipRed.png', 'number': 0},
                 8: {'value': 1, 'img': 'ChipWhite.png', 'number': 0}}

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
                textRect.center = ((screen_width / (np.ceil(len(self.possible_agents) / 2) + 1) * np.ceil((i + 1) / 2)), calculate_height(screen_height, 4, 1, tile_size, -(22 / 20)))
            else:
                textRect.center = ((screen_width / (np.ceil(len(self.possible_agents) / 2) + 1) * np.ceil((i + 1) / 2)), calculate_height(screen_height, 4, 3, tile_size, (23 / 20)))
            self.screen.blit(text, textRect)

            # Load and blit number of poker chips for each player
            font = get_font(os.path.join('font', 'Minecraft.ttf'), 24)
            text = font.render(str(state['my_chips']), True, white)
            textRect = text.get_rect()

            # Calculate number of each chip
            total = (state['my_chips'])
            height = 0
            for key in chips:
                num = total / chips[key]['value']
                chips[key]['number'] = int(num)
                total %= chips[key]['value']

                chip_img = get_image(os.path.join('img', chips[key]['img']))
                chip_img = pygame.transform.scale(chip_img, (int(tile_size / 2), int(tile_size * 16 / 45)))

                # Blit poker chip img
                for j in range(0, int(chips[key]['number'])):
                    if i % 2 == 0:
                        self.screen.blit(chip_img, ((calculate_width(self, screen_width, i) + tile_size * (8 / 10)), calculate_height(screen_height, 4, 1, tile_size, -1 / 2) - ((j + height) * tile_size / 15)))
                    else:
                        self.screen.blit(chip_img, ((calculate_width(self, screen_width, i) + tile_size * (8 / 10)), calculate_height(screen_height, 4, 3, tile_size, 1 / 2) - ((j + height) * tile_size / 15)))
                height += chips[key]['number']

            # Blit text number
            if i % 2 == 0:
                textRect.center = ((calculate_width(self, screen_width, i) + tile_size * (21 / 20)), calculate_height(screen_height, 4, 1, tile_size, -1 / 2) - ((height + 1) * tile_size / 15))
            else:
                textRect.center = ((calculate_width(self, screen_width, i) + tile_size * (21 / 20)), calculate_height(screen_height, 4, 3, tile_size, 1 / 2) - ((height + 1) * tile_size / 15))
            self.screen.blit(text, textRect)

        # Load and blit public cards
        for i, card in enumerate(state['public_cards']):
            card_img = get_image(os.path.join('img', card + '.png'))
            card_img = pygame.transform.scale(card_img, (int(tile_size * (142 / 197)), int(tile_size)))
            if len(state['public_cards']) <= 3:
                self.screen.blit(card_img, (((((screen_width / 2) + (tile_size * 31 / 616)) - calculate_offset(state['public_cards'], i, tile_size)), calculate_height(screen_height, 2, 1, tile_size, -(1 / 2)))))
            else:
                if i <= 2:
                    self.screen.blit(card_img, (((((screen_width / 2) + (tile_size * 31 / 616)) - calculate_offset(state['public_cards'][:3], i, tile_size)), calculate_height(screen_height, 2, 1, tile_size, -21 / 20))))
                else:
                    self.screen.blit(card_img, (((((screen_width / 2) + (tile_size * 31 / 616)) - calculate_offset(state['public_cards'][3:], i - 3, tile_size)), calculate_height(screen_height, 2, 1, tile_size, 1 / 20))))

        if mode == "human":
            pygame.display.update()

        observation = np.array(pygame.surfarray.pixels3d(self.screen))

        return np.transpose(observation, axes=(1, 0, 2)) if mode == "rgb_array" else None
