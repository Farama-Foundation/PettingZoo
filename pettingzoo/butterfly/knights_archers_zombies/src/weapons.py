import math
import os

import pygame

from . import constants as const
from .img import get_image


class Arrow(pygame.sprite.Sprite):
    def __init__(self, archer):
        super().__init__()
        self.archer = archer
        self.image = get_image(os.path.join("img", "arrow.png"))
        self.rect = self.image.get_rect(center=self.archer.pos)
        self.image = pygame.transform.rotate(self.image, self.archer.angle)

        self.pos = pygame.Vector2(self.archer.rect.center)
        self.fire_direction = self.archer.direction

        # reset the archer timeout when arrow fired
        archer.weapon_timeout = 0

    def update(self):
        if self.archer.alive:
            self.pos += self.fire_direction * const.ARROW_SPEED
            self.rect.center = self.pos
        else:
            self.rect.x = -100

    def is_active(self):
        if not self.archer.alive:
            return False
        if self.rect.x < 0 or self.rect.y < 0:
            return False
        if self.rect.x > const.SCREEN_WIDTH or self.rect.y > const.SCREEN_HEIGHT:
            return False
        return True


class Sword(pygame.sprite.Sprite):
    def __init__(self, knight):
        # the sword is actually a mace, but we refer to it as sword everywhere
        super().__init__()
        self.knight = knight
        self.image = get_image(os.path.join("img", "mace.png"))
        self.rect = self.image.get_rect(center=self.knight.rect.center)
        self.active = False

        # phase of the sword, starts at the left most part
        self.phase = const.MAX_PHASE

    def update(self):
        if self.knight.action == 5:
            self.active = True

        if self.active and self.knight.alive:
            # phase goes from max to min because
            # it counts positive from CCW
            if self.phase > const.MIN_PHASE:
                self.phase -= 1
                self.knight.attacking = True

                angle = math.radians(
                    self.knight.angle + 90 + const.SWORD_SPEED * self.phase
                )
                self.rect = self.image.get_rect(center=self.knight.rect.center)
                self.rect.x += (math.cos(angle) * (self.rect.width / 2)) + (
                    math.cos(angle) * (self.knight.rect.width / 2)
                )
                self.rect.y -= (math.sin(angle) * (self.rect.height / 2)) + (
                    math.sin(angle) * (self.knight.rect.height / 2)
                )
            else:
                self.phase = const.MAX_PHASE
                self.active = False
                self.knight.attacking = False

        return self.active
