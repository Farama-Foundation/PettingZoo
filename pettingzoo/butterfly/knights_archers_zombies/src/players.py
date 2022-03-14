import math
import os

import numpy as np
import pygame

from . import constants as const
from .img import get_image


class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.agent_name = None

        self.rect = pygame.Rect(0.0, 0.0, 0.0, 0.0)
        self.image = None
        self.org_image = None

        self.angle = 0
        self.pos = pygame.Vector2(self.rect.center)
        self.direction = pygame.Vector2(0, -1)

        self.alive = True
        self.score = 0

        self.is_archer = False
        self.is_knight = False

        self.speed = 0
        self.ang_rate = 0

        self.action = 6
        self.attacking = False
        self.weapon_timeout = 99

        self.weapons = pygame.sprite.Group()

    @property
    def vector_state(self):
        return np.array(
            [
                self.rect.x / const.SCREEN_WIDTH,
                self.rect.y / const.SCREEN_HEIGHT,
                *self.direction,
            ]
        )

    def update(self, action):
        self.action = action
        went_out_of_bounds = False

        if not self.attacking:
            move_angle = math.radians(self.angle + 90)
            # Up and Down movement
            if action == 1 and self.rect.y > 20:
                self.rect.x += math.cos(move_angle) * self.speed
                self.rect.y -= math.sin(move_angle) * self.speed
            elif action == 2 and self.rect.y < const.SCREEN_HEIGHT - 40:
                self.rect.x -= math.cos(move_angle) * self.speed
                self.rect.y += math.sin(move_angle) * self.speed
            # Turn CCW & CW
            elif action == 3:
                self.angle += self.ang_rate
            elif action == 4:
                self.angle -= self.ang_rate
            # weapon and do nothing
            elif action == 5 and self.alive:
                pass
            elif action == 6:
                pass

            # Clamp to stay inside the screen
            if self.rect.y < 0 or self.rect.y > (const.SCREEN_HEIGHT - 40):
                went_out_of_bounds = True

            self.rect.x = max(min(self.rect.x, const.SCREEN_WIDTH - 132), 100)
            self.rect.y = max(min(self.rect.y, const.SCREEN_HEIGHT - 40), 0)

            # add to weapon timeout when we know we're not attacking
            self.weapon_timeout += 1
        else:
            self.weapon_timeout = 0

        self.direction = pygame.Vector2(0, -1).rotate(-self.angle)
        self.image = pygame.transform.rotate(self.org_image, self.angle)
        self.rect = self.image.get_rect(center=self.rect.center)
        return went_out_of_bounds

    def offset(self, x_offset, y_offset):
        self.rect.x += x_offset
        self.rect.y += y_offset

    def is_done(self):
        return not self.alive


class Archer(Player):
    def __init__(self, agent_name):
        super().__init__()
        self.agent_name = agent_name
        self.image = get_image(os.path.join("img", "archer.png"))
        self.rect = self.image.get_rect(center=(const.ARCHER_X, const.ARCHER_Y))
        self.org_image = self.image.copy()
        self.pos = pygame.Vector2(self.rect.center)
        self.is_archer = True
        self.speed = const.ARCHER_SPEED
        self.ang_rate = const.PLAYER_ANG_RATE


class Knight(Player):
    def __init__(self, agent_name):
        super().__init__()
        self.agent_name = agent_name
        self.image = get_image(os.path.join("img", "knight.png"))
        self.rect = self.image.get_rect(center=(const.KNIGHT_X, const.KNIGHT_Y))
        self.org_image = self.image.copy()
        self.pos = pygame.Vector2(self.rect.center)
        self.is_knight = True
        self.speed = const.KNIGHT_SPEED
        self.ang_rate = const.PLAYER_ANG_RATE
