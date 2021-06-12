from pettingzoo import AECEnv
from pettingzoo.utils.agent_selector import agent_selector
from gym import spaces
import rlcard
import random
from rlcard.utils.utils import print_card
import numpy as np
from pettingzoo.utils import wrappers
from .rlcard_base import RLCardBase
import os


def get_image(path):
    import pygame
    from os import path as os_path
    cwd = os_path.dirname(__file__)
    image = pygame.image.load(cwd + '/' + path)
    return image


def env(**kwargs):
    env = raw_env(**kwargs)
    env = wrappers.TerminateIllegalWrapper(env, illegal_reward=-1)
    env = wrappers.AssertOutOfBoundsWrapper(env)
    env = wrappers.OrderEnforcingWrapper(env)
    return env


class raw_env(RLCardBase):

    metadata = {'render.modes': ['human', 'rgb_array'], "name": "texas_holdem_v3"}

    def __init__(self):
        super().__init__("limit-holdem", 2, (72,))

    def render(self, mode='human'):
        screen_width = 1600
        screen_height = 1200
        if mode == "human":
            import pygame

            if self.screen is None:
                pygame.init()
                self.screen = pygame.display.set_mode((screen_width, screen_height))

            pygame.event.get()
            # Load and scale all of the necessary images
            tile_size = screen_width / 10

            for i, player in enumerate(self.possible_agents):
                state = self.env.game.get_state(self._name_to_int(player))
                for j, card in enumerate(state['hand']):
                    card_img = get_image(os.path.join('img', card + '.png'))
                    card_img = pygame.transform.scale(card_img, (int(tile_size), int(tile_size)))
                    self.screen.blit(card_img, ((j * (tile_size), i * (tile_size))))

            # board_img = get_image(os.path.join('img', 'Connect4Board.png'))
            # board_img = pygame.transform.scale(board_img, ((int(screen_width)), int(screen_height)))

            # self.screen.blit(board_img, (0, 0))

            pygame.display.update()

        observation = np.array(pygame.surfarray.pixels3d(self.screen))

        return np.transpose(observation, axes=(1, 0, 2)) if mode == "rgb_array" else None
        # for player in self.possible_agents:

        #     print("\n=============== {}'s Hand ===============".format(player))
        #     print(state['hand'])
        #     print("\n{}'s Chips: {}".format(player, state['my_chips']))
        # print('\n================= Public Cards =================')
        # print_card(state['public_cards']) if state['public_cards'] else print('No public cards.')
        # print('\n')
