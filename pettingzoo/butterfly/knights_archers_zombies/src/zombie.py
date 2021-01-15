import os
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = 'hide'
import pygame
import os

ZOMBIE_Y_SPEED = 5
ZOMBIE_X_SPEED = 30
WIDTH = 1280


class Zombie(pygame.sprite.Sprite):

    def __init__(self, randomizer):
        super().__init__()
        img_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'img'))
        self.image = pygame.image.load(os.path.join(img_path, 'zombie.png'))
        self.rect = self.image.get_rect(center=(50, 50))
        self.randomizer = randomizer

    def update(self):
        rand_x = self.randomizer.randint(0, 10)

        # Wobbling in X-Y Direction
        self.rect.y += ZOMBIE_Y_SPEED

        if (self.rect.y % 15 == 0):
            if self.rect.x > 15 and self.rect.x < 1265:
                if rand_x in [1, 3, 6]:
                    self.rect.x += ZOMBIE_X_SPEED
                elif rand_x in [2, 4, 5, 8]:
                    self.rect.x -= ZOMBIE_X_SPEED

            # Bringing the Zombies back on the Screen
            else:
                if self.rect.x <= 15:
                    self.rect.x += 2 * ZOMBIE_X_SPEED
                elif self.rect.x >= 1265:
                    self.rect.x -= 2 * ZOMBIE_X_SPEED

        # Clamp to stay inside the screen
        self.rect.x = max(min(self.rect.x, WIDTH - 100), 100)
