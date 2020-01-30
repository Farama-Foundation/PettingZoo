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

    def __init__(self):
        super().__init__()
        # rand_x = random.randint(20, 1260)
        img_path = os.path.abspath(os.path.join(os.path.dirname( __file__ ), '..', 'img'))
        self.image = pygame.image.load(os.path.join(img_path, 'archer.png'))
        self.rect = self.image.get_rect(center=(ARCHER_X, ARCHER_Y))
        self.org_image = self.image.copy()
        self.angle = 0
        self.pos = pygame.Vector2(self.rect.center)
        self.direction = pygame.Vector2(0, -1)
        self.attacking = False # disable movement during attacking
        self.weapon = Arrow(self)
        self.alive = True

    def update(self, action):
        keys = pygame.key.get_pressed()
        
        if not self.attacking:
            move_angle = math.radians(self.angle + 90)
            # Up and Down movement
            if action == 1 and self.rect.y > 20:
                self.rect.x += math.cos(move_angle) * KNIGHT_SPEED
                self.rect.y -= math.sin(move_angle) * KNIGHT_SPEED
            elif action == 2 and self.rect.y < HEIGHT - 40:
                self.rect.x += math.cos(move_angle) * KNIGHT_SPEED
                self.rect.y += math.sin(move_angle) * KNIGHT_SPEED
            # Turn CCW & CW
            elif action == 3:
                self.angle += ANGLE_RATE
            elif action == 4:
                self.angle -= ANGLE_RATE
            elif action == 5 and self.alive:
                self.weapon.fired = True
                # self.attacking = True # gets reset to False in weapon attack

            # Clamp to stay inside the screen
            self.rect.x = max(min(self.rect.x, WIDTH - 32), 0)
            self.rect.y = max(min(self.rect.y, HEIGHT - 40), 0)

        self.direction = pygame.Vector2(0, -1).rotate(-self.angle)
        self.image = pygame.transform.rotate(self.org_image, self.angle)
        self.rect = self.image.get_rect(center=self.rect.center)

    def offset(self, x_offset, y_offset):
        self.rect.x += x_offset
        self.rect.y += y_offset

    def is_done(self):
        return self.alive


class Knight(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        img_path = os.path.abspath(os.path.join(os.path.dirname( __file__ ), '..', 'img'))
        self.image = pygame.image.load(os.path.join(img_path, 'knight.png'))
        self.rect = self.image.get_rect(center=(KNIGHT_X, KNIGHT_Y))
        self.org_image = self.image.copy()
        self.angle = 0
        self.pos = pygame.Vector2(self.rect.center)
        self.direction = pygame.Vector2(1, 0)
        # self.radius = radius
        self.attacking = False # Used to disable movement during attacking
        self.attack_phase = -5
        self.weapon = Sword(self)
        self.alive = True # This flag is used to immediately delete the mace object when the knight dies
        self.action = -1

    def update(self, action):
        keys = pygame.key.get_pressed()
        self.action = action

        if not self.attacking:
            move_angle = math.radians(self.angle + 90)
            # Up and Down movement
            if action == 1 and self.rect.y > 20:
                self.rect.x += math.cos(move_angle) * KNIGHT_SPEED
                self.rect.y -= math.sin(move_angle) * KNIGHT_SPEED
            elif action == 2 and self.rect.y < HEIGHT - 40:
                self.rect.x += math.cos(move_angle) * KNIGHT_SPEED
                self.rect.y += math.sin(move_angle) * KNIGHT_SPEED
            # Turn CCW & CW
            elif action == 3:
                self.angle += ANGLE_RATE
            elif action == 4:
                self.angle -= ANGLE_RATE
            elif action == 5:
                self.attacking = True # gets reset to False in weapon attack

            # Clamp to stay inside the screen
            self.rect.x = max(min(self.rect.x, WIDTH - 32), 0)
            self.rect.y = max(min(self.rect.y, HEIGHT - 40), 0)
            
        self.direction = pygame.Vector2(0, -1).rotate(-self.angle)
        self.image = pygame.transform.rotate(self.org_image, self.angle)
        self.rect = self.image.get_rect(center=self.rect.center)

    def offset(self, x_offset, y_offset):
        self.rect.x += x_offset
        self.rect.y += y_offset

    def is_done(self):
        return self.alive