import os

import numpy as np
import pygame

from pettingzoo.butterfly.knights_archers_zombies.src import constants as const
from pettingzoo.butterfly.knights_archers_zombies.src.img import get_image


class Zombie(pygame.sprite.Sprite):
    def __init__(self, randomizer):
        super().__init__()
        self.image = get_image(os.path.join("img", "zombie.png"))
        self.rect = self.image.get_rect(center=(50, 50))
        self.randomizer = randomizer

        self.x_lims = [const.SCREEN_UNITS, const.SCREEN_WIDTH - const.SCREEN_UNITS]

    @property
    def vector_state(self):
        return np.array(
            [
                self.rect.x / const.SCREEN_WIDTH,
                self.rect.y / const.SCREEN_HEIGHT,
                0.0,
                1.0,
            ]
        )

    def update(self):
        rand_x = self.randomizer.integers(0, 10)

        self.rect.y += const.ZOMBIE_Y_SPEED

        # Wobbling in X-Y Direction
        if self.rect.y % const.SCREEN_UNITS == 0:
            if self.rect.x > self.x_lims[0] and self.rect.x < self.x_lims[1]:
                if rand_x in [1, 3, 6]:
                    self.rect.x += const.ZOMBIE_X_SPEED
                elif rand_x in [2, 4, 5, 8]:
                    self.rect.x -= const.ZOMBIE_X_SPEED

            # Bringing the Zombies back on the Screen
            else:
                if self.rect.x <= self.x_lims[0]:
                    self.rect.x += 2 * const.ZOMBIE_X_SPEED
                elif self.rect.x >= self.x_lims[1]:
                    self.rect.x -= 2 * const.ZOMBIE_X_SPEED

        # Clamp to stay inside the screen
        self.rect.x = max(min(self.rect.x, const.SCREEN_WIDTH - 100), 100)
