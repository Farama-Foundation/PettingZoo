import os
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = 'hide'
import pygame
import math
import os

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
        img_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'img'))
        self.image = pygame.image.load(os.path.join(img_path, 'arrow.png'))
        self.archer = archer
        self.rect = self.image.get_rect(center=self.archer.pos)
        self.direction = self.archer.direction
        self.pos = pygame.Vector2(self.archer.rect.center)
        self.fired = True
        self.angle = self.archer.angle
        self.image = pygame.transform.rotate(self.image, self.angle)

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

    def __init__(self, knight):
        super().__init__()
        self.image = pygame.Surface((4, 25), pygame.SRCALPHA)
        # self.image.fill(GRAY)
        img_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'img'))
        self.image = pygame.image.load(os.path.join(img_path, 'mace.png'))
        self.knight = knight
        self.rect = self.image.get_rect(center=self.knight.rect.center)
        self.direction = self.knight.direction
        self.org_image = self.image.copy()
        self.angle = self.knight.angle
        self.pos = self.knight.pos
        self.speed = 20
        self.phase = 3
        self.MIN_PHASE = -3
        self.MAX_PHASE = 3
        self.active = False

    def update(self):
        # Attack
        if self.knight.action == 5:
            self.active = True

        if self.active and self.knight.alive:
            if self.phase > self.MIN_PHASE:
                self.phase -= 1
                self.knight.attacking = True

                angle = math.radians(self.knight.angle + 90 + self.speed * self.phase)
                self.rect = self.image.get_rect(center=self.knight.rect.center)
                self.rect.x += (math.cos(angle) * (self.rect.width / 2)) + (math.cos(angle) * (self.knight.rect.width / 2))
                self.rect.y -= (math.sin(angle) * (self.rect.height / 2)) + (math.sin(angle) * (self.knight.rect.height / 2))
            else:
                self.phase = self.MAX_PHASE
                self.active = False
                self.knight.attacking = False

        return self.active
