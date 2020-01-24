#!usr/bin/env python3

# Importing Libraries
import pygame
import math

# Game Constants
BLACK = (0, 0, 0)
GRAY = (200, 200, 200)
ARROW_SPEED = 45
SPEED_VAL = 3
ANGLE_RATE = 10
KNIGHT_SPEED = 5
HEIGHT = 720
WIDTH = 1280
i = 1

class Arrow(pygame.sprite.Sprite):

    def __init__(self, archer):
        super().__init__()
        self.image = pygame.Surface([6, 6])
        self.image.fill(BLACK)
        self.archer = archer
        self.rect = self.image.get_rect(center=self.archer.pos)
        self.direction = self.archer.direction
        self.pos = pygame.Vector2(self.archer.rect.center)

    def update(self):
        self.pos += self.direction * ARROW_SPEED
        self.rect.center = self.pos


class Sword(pygame.sprite.Sprite):

    def __init__(self, knight, sword_rect):
        super().__init__()
        self.i = i
        self.image = sword_rect
        self.image.fill(GRAY)
        self.knight = knight
        self.rect = self.image.get_rect(center = self.knight.rect.center)
        self.direction = self.knight.direction
        self.org_image = self.image.copy()
        self.angle = self.knight.angle
        self.pos = self.knight.pos

    def update(self):
        keys = pygame.key.get_pressed()
        self.i += 1

        self.angle = self.knight.angle
        # Get the angle converted to normal unit circle angles and in radians.
        rota_angle = math.radians(self.angle  + 90)

        self.rect = self.image.get_rect(center = self.knight.rect.center)
        self.image = pygame.transform.rotate(self.org_image, self.angle)
        self.rect.x += (math.cos(rota_angle) * (self.rect.width / 2)) + (math.cos(rota_angle) * (self.knight.rect.width / 2))
        self.rect.y -= (math.sin(rota_angle) * (self.rect.height / 2)) + (math.sin(rota_angle) * (self.knight.rect.height / 2))

        self.direction = self.knight.direction

        return self.i