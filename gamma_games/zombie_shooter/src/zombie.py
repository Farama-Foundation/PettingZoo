#!usr/bin/env python3

# Importing Libraries
import pygame
import random

# Game Constants
ZOMBIE_Y_SPEED = 5
ZOMBIE_X_SPEED = 30

class Zombie(pygame.sprite.Sprite):

    def __init__(self, color, circle):
        super().__init__()
        self.image = circle
        self.rect = self.image.get_rect(center=(50, 50))

    def update(self):
        rand_x = random.randint(0, 10)

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
                    self.rect.x += 2*ZOMBIE_X_SPEED
                elif self.rect.x >= 1265:
                    self.rect.x -= 2*ZOMBIE_X_SPEED