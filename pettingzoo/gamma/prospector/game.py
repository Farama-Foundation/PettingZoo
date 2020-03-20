import pygame
import pygame.math
from pygame.locals import *
import pygame.font

import os
from random import random, uniform

SCREEN_SIZE = (1002, 699)  # Looks weird, but is the size of the background image
RED = (255, 0, 0)
CHEST_COLOR_1 = (185, 115, 34)
CHEST_COLOR_2 = (3, 252, 252)
WHITE = (255, 255, 255)
BOTTOM_BLUE = (0, 163, 232)

GOLD_IMG_SIZE = 32

CHEST_SIZE = (100, 97)

BASE_VECTOR = pygame.Vector2(1, 0)

MOVE_SPEED = 10


def load_image(path: list) -> pygame.Surface:  # All images stored in data/
    img = pygame.image.load(os.path.join("data", *path))
    img = img.convert_alpha()

    return img


class Gold:
    def __init__(self):
        self.tag = "gold"

        self.surf = load_image(["gold", "6.png"])
        self.surf_rect = self.surf.get_rect()

        self.active = True

    def update(self, x, y):
        # Offsets to center the golden nugget in the image of `agent1.jpg`
        if self.active:
            self.surf_rect.x = x + 10
            self.surf_rect.y = y + 9

    def draw(self, screen: pygame.Surface):
        if self.active:
            screen.blit(self.surf, self.surf_rect)

    def deactivate(self):
        self.active = False
        self.surf_rect.x = 0
        self.surf_rect.y = 0


class Prospector:
    def __init__(self):
        self.x = uniform(50, SCREEN_SIZE[0] - 50)
        self.y = uniform(200, 400)

        self.surf = load_image(["agent1.jpg"])
        self.surf_orig = self.surf.copy()
        self.surf_rect = self.surf.get_rect()

        self.surf_rect.x = self.x
        self.surf_rect.y = self.y

        # Currently unused, would need for rotation
        self.direc = pygame.Vector2()
        self.direc.xy = 1, 0

        self.nugget = None

    def update(self, keys, water):
        # forward = 0
        # if keys[K_UP]:
        #     forward = MOVE_SPEED
        # elif keys[K_DOWN]:
        #     forward = -MOVE_SPEED

        # if keys[K_LEFT]:
        #     self.vel = self.vel.rotate_ip(15)
        # elif keys[K_RIGHT]:
        #     self.vel = self.vel.rotate_ip(-15)

        # Move prospector -------------------------------------
        x = y = theta = 0
        if keys[K_w]:
            y = -MOVE_SPEED
        elif keys[K_s]:
            y = MOVE_SPEED

        if keys[K_a]:
            x = -MOVE_SPEED
        elif keys[K_d]:
            x = MOVE_SPEED

        if keys[K_LEFT]:
            # self.vel = self.vel.rotate_ip(15)
            theta = -15
        elif keys[K_RIGHT]:
            # self.vel = self.vel.rotate_ip(-15)
            theta = 15

        self.direc.rotate_ip(theta)

        angle = self.direc.angle_to(BASE_VECTOR)

        center = self.surf_rect.center

        self.surf = pygame.transform.rotate(self.surf_orig, angle)

        self.surf_rect = self.surf.get_rect(center=center)

        self.surf_rect.move_ip(x, y)
        # self.surf = pygame.transform.rotate(self.surf, theta)
        # new_rect = self.surf.get_rect()
        # self.surf_rect = pygame.Rect(*self.surf_rect.topleft, *new_rect.size)

        print(self.surf_rect.size)

        # Check for collisions ------
        # NO NEED (water generates nuggets)
        # if self.nugget is None:
        #     # If we are colliding with a gold nugget, set it to us
        #     for g in gold:
        #         if self.surf_rect.colliderect(g.surf_rect):
        #             self.nugget = g
        #             break

        # Chest collision ---------- MOVE TO BANKER
        # if self.nugget is not None:
        #     for c in chests:
        #         if self.surf_rect.colliderect(c.rect):
        #             c.score()
        #             self.nugget.deactivate()
        #             self.nugget = None

        #             break

        # Water collision ----------------------------
        if self.nugget is None:
            if self.surf_rect.colliderect(water.rect):
                self.nugget = Gold()

        # Correct movement to fit in bounds of screen ------------
        if self.surf_rect.x < 0:
            self.surf_rect.x = 0
        elif self.surf_rect.x > SCREEN_SIZE[0] - self.surf_rect.width:
            self.surf_rect.x = SCREEN_SIZE[0] - self.surf_rect.width

        if self.surf_rect.y < CHEST_SIZE[1]:
            self.surf_rect.y = CHEST_SIZE[1]
        elif (
            self.surf_rect.y
            > (SCREEN_SIZE[1] - self.surf_rect.height) - water.rect.height
        ):
            self.surf_rect.y = (
                SCREEN_SIZE[1] - self.surf_rect.height
            ) - water.rect.height

        # Update gold nugget position if we have one
        if self.nugget is not None:
            self.nugget.update(*self.surf_rect.topleft)

        # print(self.nugget)

    def draw(self, screen: pygame.Surface):
        screen.blit(self.surf, self.surf_rect)
        if self.nugget is not None:
            self.nugget.draw(screen)


class Chest:
    def __init__(self, x, y, num, font):
        self.x, self.y = x, y

        self.rect = pygame.Rect(x, y, *CHEST_SIZE)

        self.count = 0
        self.num = num

        self.font = font
        self.text = None
        self.text_rect = pygame.Rect(x + 5, y + 5, 100, 100)
        self._re_render_text()

    def draw(self, screen: pygame.Surface):
        pygame.draw.rect(screen, CHEST_COLOR_2, self.rect)
        # Text render
        screen.blit(self.text, self.text_rect)

    def score(self):
        self.count += 1
        self._re_render_text()

    def _re_render_text(self):
        self.text = self.font.render(str(self.count), True, WHITE)

    def __str__(self):
        return f"Chest {self.num}: {self.count}"


class Water:
    def __init__(self):
        self.tag = "water"
        self.rect = pygame.Rect(0, SCREEN_SIZE[1] - 96, 1002, 96)


class Game:
    def __init__(self):
        # Pygame setup
        self.screen = pygame.display.set_mode(SCREEN_SIZE)
        pygame.display.set_caption("Prospector")

        # Used for making movement framerate-independent.
        self.clock = pygame.time.Clock()
        self.framerate = 60

        # Background stuff
        self.background = load_image(["background.jpg"])
        self.background_rect = self.background.get_rect()

        self.water = Water()

        # Prospectors
        self.prospec_1 = Prospector()

        # Fonts setup
        default = pygame.font.get_default_font()
        font = pygame.font.Font(default, 50)

        # Chests setup
        self.chests = []
        self.chests.append(Chest(143 * 1, 0, 1, font))
        self.chests.append(Chest(143 * 3, 0, 2, font))
        self.chests.append(Chest(143 * 5, 0, 3, font))

        # Gold token initialization

    def run(self):
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == QUIT or (event.type == KEYDOWN and event.key == K_q):
                    running = False
                if event.type == KEYDOWN and event.key == K_p:
                    print(self.chests[0], self.chests[1], self.chests[2])

            time_delta = self.clock.tick(self.framerate)
            keys = pygame.key.get_pressed()

            # Updating --------------------------------------------
            # self.prospec_1.update(keys, self.gold, self.chests)

            self.prospec_1.update(keys, self.water)

            # Drawing ---------------------------------------------
            self.screen.blit(self.background, self.background_rect)

            self.prospec_1.draw(self.screen)

            for c in self.chests:
                c.draw(self.screen)

            pygame.display.flip()


def main():
    pygame.font.init()
    pygame.init()
    game = Game()
    game.run()


if __name__ == "__main__":
    main()
