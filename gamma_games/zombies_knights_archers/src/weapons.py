#!usr/bin/env python3

# Importing Libraries
import pygame
import math
import os

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
        img_path = os.path.abspath(os.path.join(os.path.dirname( __file__ ), '..', 'img'))
        self.image = pygame.image.load(os.path.join(img_path, 'arrow.png'))
        self.archer = archer
        self.rect = self.image.get_rect(center=self.archer.pos)
        self.direction = self.archer.direction
        self.pos = pygame.Vector2(self.archer.rect.center)
        self.fired = True

    def update(self):
        print('arrow update')
        print(self.pos)
        self.pos += self.direction * ARROW_SPEED
        self.rect.center = self.pos


class Sword(pygame.sprite.Sprite):

    def __init__(self, knight):
        super().__init__()
        self.i = i # TODO: remove this. Does it break the code if I remove it?
        self.image = pygame.Surface((4, 25), pygame.SRCALPHA)
        # self.image.fill(GRAY)
        img_path = os.path.abspath(os.path.join(os.path.dirname( __file__ ), '..', 'img'))
        self.image = pygame.image.load(os.path.join(img_path, 'mace.png'))
        self.knight = knight
        self.rect = self.image.get_rect(center = self.knight.rect.center)
        self.direction = self.knight.direction
        self.org_image = self.image.copy()
        self.angle = self.knight.angle
        self.pos = self.knight.pos
        self.speed = 5
        self.phase = 5
        self.active = False

    def update(self):
        keys = pygame.key.get_pressed()
        print('sword update')

        # Attack
        if self.knight.action == 5:
            self.active = True

        if self.active and self.knight.alive:
            if self.phase > -5:
                self.phase -= 1
                self.knight.attacking = True

                angle = math.radians(self.knight.angle + 90 + self.speed * self.phase)
                self.rect = self.image.get_rect(center = self.knight.rect.center)
                self.rect.x += (math.cos(angle) * (self.rect.width / 2)) + (math.cos(angle) * (self.knight.rect.width / 2))
                self.rect.y -= (math.sin(angle) * (self.rect.height / 2)) + (math.sin(angle) * (self.knight.rect.height / 2))
            else:
                self.phase = 5
                self.active = False
                self.knight.attacking = False
                self.knight.action = -1
                
        return self.active