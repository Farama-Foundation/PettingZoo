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
        self.rect = self.image.get_rect(center=self.knight.rect.center)
        self.direction = self.knight.direction
        self.org_image = self.image.copy()
        self.angle = self.knight.angle
        self.pos = self.knight.pos

    def update(self):
        keys = pygame.key.get_pressed()
        self.i += 1
        self.rect.y = self.knight.rect.y - 25
        self.rect.x = self.knight.rect.x + 29

        if (keys[pygame.K_j] and self.rect.x > 0):
            self.rect.x -= KNIGHT_SPEED
        if (keys[pygame.K_l] and self.rect.x < WIDTH - 60):
            self.rect.x += KNIGHT_SPEED
        if (keys[pygame.K_i] and self.rect.y > 20):
            self.rect.y -= KNIGHT_SPEED
        if (keys[pygame.K_k] and self.rect.y < HEIGHT - 40):
            self.rect.y += KNIGHT_SPEED

        # Turn CCW & CW
        if keys[pygame.K_u]:
            # print(self.angle)
            self.angle += ANGLE_RATE
            self.rect.center = self.knight.rect.center
            # self.angle = (self.angle * math.pi) / 180
            # self.rect.bottom = self.rect.y * math.cos(-self.angle) - (self.knight.rect.x + 29) * math.sin(-self.angle)
            # # self.rect.x = self.rect.y * math.sin(self.angle) + (self.knight.rect.x + 29) * math.cos(self.angle) - 10
            # self.angle = (self.angle * 180) / math.pi

        if keys[pygame.K_o]:
            # print(self.angle)
            self.angle -= ANGLE_RATE
            self.rect.center = self.knight.rect.center
            # self.rect.bottom = self.rect.y * math.cos(-self.angle) - (self.knight.rect.x + 29) * math.sin(-self.angle)
            # # self.rect.x = self.rect.y * math.sin(self.angle) + (self.knight.rect.x + 29) * math.cos(self.angle) - 10
            # self.rect.y = self.rect.y + 100
            # self.rect.x = self.rect.x + 30

        self.direction = self.knight.direction
        self.rect = self.image.get_rect(center=self.rect.center)

        # self.rect = self.image.get_rect(center=(self.knight.rect.x + 20, self.knight.rect.y + 20))
        self.image = pygame.transform.rotate(self.org_image, self.angle)

        return self.i