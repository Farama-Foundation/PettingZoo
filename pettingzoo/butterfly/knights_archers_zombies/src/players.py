import os
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = 'hide'
import pygame
import math
import os
from .weapons import Arrow, Sword

WIDTH = 1280
HEIGHT = 720
ARCHER_SPEED = 25
KNIGHT_SPEED = 25
ARCHER_X, ARCHER_Y = 400, 610
KNIGHT_X, KNIGHT_Y = 800, 610
ANGLE_RATE = 10


class Archer(pygame.sprite.Sprite):

    def __init__(self, agent_name):
        super().__init__()
        img_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'img'))
        self.image = pygame.image.load(os.path.join(img_path, 'archer.png'))
        self.rect = self.image.get_rect(center=(ARCHER_X, ARCHER_Y))
        self.org_image = self.image.copy()
        self.angle = 0
        self.pos = pygame.Vector2(self.rect.center)
        self.direction = pygame.Vector2(0, -1)
        self.attacking = False  # disable movement during attacking
        self.weapon = Arrow(self)
        self.alive = True
        self.score = 0
        self.is_archer = True
        self.is_knight = False
        self.agent_name = agent_name

    def update(self, action):
        went_out_of_bounds = False

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
            elif action == 6:
                pass

            # Clamp to stay inside the screen
            if self.rect.y < 0 or self.rect.y > (HEIGHT - 40):
                went_out_of_bounds = True

            self.rect.x = max(min(self.rect.x, WIDTH - 132), 100)
            self.rect.y = max(min(self.rect.y, HEIGHT - 40), 0)

        self.direction = pygame.Vector2(0, -1).rotate(-self.angle)
        self.image = pygame.transform.rotate(self.org_image, self.angle)
        self.rect = self.image.get_rect(center=self.rect.center)
        return went_out_of_bounds

    def offset(self, x_offset, y_offset):
        self.rect.x += x_offset
        self.rect.y += y_offset

    def is_done(self):
        return not self.alive


class Knight(pygame.sprite.Sprite):
    def __init__(self, agent_name):
        super().__init__()
        img_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'img'))
        self.image = pygame.image.load(os.path.join(img_path, 'knight.png'))
        self.rect = self.image.get_rect(center=(KNIGHT_X, KNIGHT_Y))
        self.org_image = self.image.copy()
        self.angle = 0
        self.pos = pygame.Vector2(self.rect.center)
        self.direction = pygame.Vector2(1, 0)
        # self.radius = radius
        self.attacking = False  # Used to disable movement during attacking
        self.attack_phase = -5
        self.weapon = Sword(self)
        self.alive = True  # This flag is used to immediately delete the mace object when the knight dies
        self.action = -1
        self.score = 0
        self.is_archer = False
        self.is_knight = True
        self.agent_name = agent_name

    def update(self, action):
        self.action = action
        went_out_of_bounds = False
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
                self.attacking = True  # gets reset to False in weapon attack
            elif action == 6:
                pass

            # Clamp to stay inside the screen
            if self.rect.y < 0 or self.rect.y > (HEIGHT - 40):
                went_out_of_bounds = True

            self.rect.x = max(min(self.rect.x, WIDTH - 132), 100)
            self.rect.y = max(min(self.rect.y, HEIGHT - 40), 0)

        self.direction = pygame.Vector2(0, -1).rotate(-self.angle)
        self.image = pygame.transform.rotate(self.org_image, self.angle)
        self.rect = self.image.get_rect(center=self.rect.center)

        return went_out_of_bounds

    def offset(self, x_offset, y_offset):
        self.rect.x += x_offset
        self.rect.y += y_offset

    def is_done(self):
        return not self.alive
