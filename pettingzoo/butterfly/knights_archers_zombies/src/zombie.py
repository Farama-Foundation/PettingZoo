import os

import pygame

from .img import get_image

ZOMBIE_Y_SPEED = 5
ZOMBIE_X_SPEED = 30
WIDTH = 1280


class Zombie(pygame.sprite.Sprite):

    def __init__(self, randomizer, FPS):
        super().__init__()
        self.image = get_image(os.path.join('img', 'zombie.png'))
        self.rect = self.image.get_rect(center=(50, 50))
        self.randomizer = randomizer

        self.zombie_y_speed = ZOMBIE_Y_SPEED * 15. / FPS
        self.zombie_x_speed = ZOMBIE_X_SPEED * 15. / FPS

        if self.zombie_y_speed % 1. != 0.:
            raise ValueError(f'FPS of {FPS} leads to decimal place value of {self.zombie_y_speed} for zombie y speed.')
        if self.zombie_x_speed % 1. != 0.:
            raise ValueError(f'FPS of {FPS} leads to decimal place value of {self.zombie_x_speed} for zombie y speed.')

        self.zombie_y_speed = int(self.zombie_y_speed)
        self.zombie_x_speed = int(self.zombie_x_speed)


    def update(self):
        rand_x = self.randomizer.randint(0, 10)

        self.rect.y += self.zombie_y_speed

        # Wobbling in X-Y Direction
        if (self.rect.y % 15 == 0):
            if self.rect.x > 15 and self.rect.x < 1265:
                if rand_x in [1, 3, 6]:
                    self.rect.x += self.zombie_x_speed
                elif rand_x in [2, 4, 5, 8]:
                    self.rect.x -= self.zombie_x_speed

            # Bringing the Zombies back on the Screen
            else:
                if self.rect.x <= 15:
                    self.rect.x += 2 * self.zombie_x_speed
                elif self.rect.x >= 1265:
                    self.rect.x -= 2 * self.zombie_x_speed

        # Clamp to stay inside the screen
        self.rect.x = max(min(self.rect.x, WIDTH - 100), 100)
