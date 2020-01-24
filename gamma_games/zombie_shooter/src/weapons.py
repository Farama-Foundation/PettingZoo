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

    def __init__(self, archer, radius):
        super().__init__()
        self.image = pygame.Surface([6, 6])
        self.image.fill(BLACK)
        self.archer = archer
        self.rect = self.image.get_rect(center=self.archer.pos)
        self.direction = self.archer.direction
        self.pos = pygame.Vector2(self.archer.rect.center)
        self.radius = radius

    def update(self):
        self.pos += self.direction * ARROW_SPEED
        self.rect.center = self.pos


class Sword(pygame.sprite.Sprite):

    def __init__(self, knight, radius):
        super().__init__()
        self.i = i
        self.image = pygame.Surface((4, 25), pygame.SRCALPHA)
        # self.image.fill(GRAY)
        self.image = pygame.image.load("E:\\Drive\\UMD\\Research\\Parameter Sharing\\rlgames\\gamma_games\\zombie_shooter\\img\\mace.png")
        self.knight = knight
        self.rect = self.image.get_rect(center = self.knight.rect.center)
        self.direction = self.knight.direction
        self.org_image = self.image.copy()
        self.angle = self.knight.angle
        self.pos = self.knight.pos
        self.radius = radius
        self.speed = 5

    def update(self):
        # keys = pygame.key.get_pressed()
        # self.i += 1

        # self.angle = self.knight.angle
        # # Get the angle converted to normal unit circle angles and in radians.
        # rota_angle = math.radians(self.angle  + 90)

        # self.rect = self.image.get_rect(center = self.knight.rect.center)
        # self.image = pygame.transform.rotate(self.org_image, self.angle)
        # self.rect.x += (math.cos(rota_angle) * (self.rect.width / 2)) + (math.cos(rota_angle) * (self.knight.rect.width / 2))
        # self.rect.y -= (math.sin(rota_angle) * (self.rect.height / 2)) + (math.sin(rota_angle) * (self.knight.rect.height / 2))

        # self.direction = self.knight.direction

        return self.i

    def draw(self, phase):
        # TODO: hide/remove the mace when the swing is done. need to hide the sprite
        angle = math.radians(self.knight.angle + self.speed * phase) # TODO: need to add 90 to this to make it normal radians like unit circle? double check
        self.rect = self.image.get_rect(center = self.knight.rect.center)
        # self.image = pygame.transform.rotate(self.org_image, self.angle)
        self.rect.x += (math.cos(angle) * (self.rect.width / 2)) + (math.cos(angle) * (self.knight.rect.width / 2))
        self.rect.y -= (math.sin(angle) * (self.rect.height / 2)) + (math.sin(angle) * (self.knight.rect.height / 2))