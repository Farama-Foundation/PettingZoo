#!usr/bin/env python3

# Importing Libraries
import pygame
import random
import math
import os
from .weapons import Arrow, Sword

# Game Constants
WIDTH = 1280
HEIGHT = 720
ARCHER_SPEED = 25
KNIGHT_SPEED = 25
ARCHER_X, ARCHER_Y = 400, 710
KNIGHT_X, KNIGHT_Y = 800, 710
ANGLE_RATE = 10
# POS = (100, 100)

class Archer(pygame.sprite.Sprite):

    def __init__(self, red_trigon, radius):
        super().__init__()
        # rand_x = random.randint(20, 1260)
        img_path = os.path.abspath(os.path.join(os.path.dirname( __file__ ), '..', 'img'))
        self.image = pygame.image.load(os.path.join(img_path, 'archer.png'))
        self.rect = self.image.get_rect(center=(ARCHER_X, ARCHER_Y))
        self.org_image = self.image.copy()
        self.angle = 0
        self.pos = pygame.Vector2(self.rect.center)
        self.direction = pygame.Vector2(0, -1)
        self.radius = radius
        self.attacking = False # disable movement during attacking
        self.weapon = Arrow(self, radius)

    def update(self):
        keys = pygame.key.get_pressed()
        
        if not self.attacking:
            move_angle = math.radians(self.angle + 90)
            # Up and Down movement
            if (keys[pygame.K_w] and self.rect.y > 20):
                self.rect.x += math.cos(move_angle) * KNIGHT_SPEED
                self.rect.y -= math.sin(move_angle) * KNIGHT_SPEED
            if (keys[pygame.K_s] and self.rect.y < HEIGHT - 40):
                self.rect.x += math.cos(move_angle) * KNIGHT_SPEED
                self.rect.y += math.sin(move_angle) * KNIGHT_SPEED

            # Turn CCW & CW
            if keys[pygame.K_q]:
                self.angle += ANGLE_RATE
            if keys[pygame.K_e]:
                self.angle -= ANGLE_RATE

        self.direction = pygame.Vector2(0, -1).rotate(-self.angle)
        self.image = pygame.transform.rotate(self.org_image, self.angle)
        self.rect = self.image.get_rect(center=self.rect.center)


class Knight(pygame.sprite.Sprite):

    def __init__(self, blue_trigon, radius):
        super().__init__()
        img_path = os.path.abspath(os.path.join(os.path.dirname( __file__ ), '..', 'img'))
        self.image = pygame.image.load(os.path.join(img_path, 'knight2.png'))
        self.rect = self.image.get_rect(center=(KNIGHT_X, KNIGHT_Y))
        self.org_image = self.image.copy()
        self.angle = 0
        self.pos = pygame.Vector2(self.rect.center)
        self.direction = pygame.Vector2(1, 0)
        self.radius = radius
        self.attacking = False # disable movement during attacking
        self.attack_phase = -5
        self.weapon = Sword(self, radius)

    def update(self):
        keys = pygame.key.get_pressed()

        if not self.attacking:
            move_angle = math.radians(self.angle + 90)
            # Up and Down movement
            if (keys[pygame.K_i] and self.rect.y > 20):
                self.rect.x += math.cos(move_angle) * KNIGHT_SPEED
                self.rect.y -= math.sin(move_angle) * KNIGHT_SPEED
            if (keys[pygame.K_k] and self.rect.y < HEIGHT - 40):
                self.rect.x += math.cos(move_angle) * KNIGHT_SPEED
                self.rect.y += math.sin(move_angle) * KNIGHT_SPEED

            # Turn CCW & CW
            if keys[pygame.K_u]:
                self.angle += ANGLE_RATE
            if keys[pygame.K_o]:
                self.angle -= ANGLE_RATE

        self.direction = pygame.Vector2(0, -1).rotate(-self.angle)
        self.image = pygame.transform.rotate(self.org_image, self.angle)
        self.rect = self.image.get_rect(center=self.rect.center)
