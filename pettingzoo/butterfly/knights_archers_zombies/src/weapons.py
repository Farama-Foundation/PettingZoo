import math
import os

import pygame

from .img import get_image

BLACK = (0, 0, 0)
GRAY = (200, 200, 200)
ARROW_SPEED = 45
ANGLE_RATE = 10
SWORD_SPEED = 20
HEIGHT = 720
WIDTH = 1280
i = 1


class Arrow(pygame.sprite.Sprite):

    def __init__(self, archer, FPS):
        super().__init__()
        self.image = pygame.Surface([6, 6])
        self.image = get_image(os.path.join('img', 'arrow.png'))
        self.archer = archer
        self.rect = self.image.get_rect(center=self.archer.pos)
        self.direction = self.archer.direction
        self.pos = pygame.Vector2(self.archer.rect.center)
        self.fired = True
        self.angle = self.archer.angle
        self.image = pygame.transform.rotate(self.image, self.angle)

        self.arrow_speed = ARROW_SPEED * 15. / FPS
        if self.arrow_speed % 1. != 0.:
            raise ValueError(f'FPS of {FPS} leads to decimal place value of {self.arrow_speed} for arrow_speed.')
        self.arrow_speed = int(self.arrow_speed)

    def update(self):
        if self.archer.alive:
            self.pos += self.direction * ARROW_SPEED
            self.rect.center = self.pos
        else:
            self.rect.x = -100
            # self.pos = pygame.Vector2(-10, -10)

    def is_active(self):
        if not self.archer.alive:
            return False
        if self.rect.x < 0 or self.rect.y < 0:
            return False
        if self.rect.x > WIDTH or self.rect.y > HEIGHT:
            return False
        return True


class Sword(pygame.sprite.Sprite):

    def __init__(self, knight, FPS):
        super().__init__()
        self.image = pygame.Surface((4, 25), pygame.SRCALPHA)
        # self.image.fill(GRAY)
        self.image = get_image(os.path.join('img', 'mace.png'))
        self.knight = knight
        self.rect = self.image.get_rect(center=self.knight.rect.center)
        self.direction = self.knight.direction
        self.org_image = self.image.copy()
        self.angle = self.knight.angle
        self.pos = self.knight

        self.speed = SWORD_SPEED * 15. / FPS
        self.phase = 3 * 15. / FPS
        self.min_phase = -3 / 15. * FPS
        self.max_phase = 3 / 15. * FPS

        if self.speed % 1. != 0.:
            raise ValueError(f'FPS of {FPS} leads to decimal place value of {self.speed} for knight_speed.')
        if self.phase % 1. != 0.:
            raise ValueError(f'FPS of {FPS} leads to decimal place value of {self.phase} for phase.')
        if self.min_phase % 1. != 0.:
            raise ValueError(f'FPS of {FPS} leads to decimal place value of {self.min_phase} for min_phase.')
        if self.max_phase % 1. != 0.:
            raise ValueError(f'FPS of {FPS} leads to decimal place value of {self.max_phase} for max_phase.')

        self.speed = int(self.speed)
        self.phase = int(self.phase)
        self.min_phase = int(self.min_phase)
        self.max_phase = int(self.max_phase)

        self.active = False

    def update(self):
        # Attack
        if self.knight.action == 5:
            self.active = True

        if self.active and self.knight.alive:
            if self.phase > self.min_phase:
                self.phase -= 1
                self.knight.attacking = True

                angle = math.radians(self.knight.angle + 90 + self.speed * self.phase)
                self.rect = self.image.get_rect(center=self.knight.rect.center)
                self.rect.x += (math.cos(angle) * (self.rect.width / 2)) + (math.cos(angle) * (self.knight.rect.width / 2))
                self.rect.y -= (math.sin(angle) * (self.rect.height / 2)) + (math.sin(angle) * (self.knight.rect.height / 2))
            else:
                self.phase = self.max_phase
                self.active = False
                self.knight.attacking = False

        return self.active
