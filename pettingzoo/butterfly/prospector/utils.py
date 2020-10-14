import pygame as pg
from pymunk import Vec2d

import os
import math

from . import constants as const


def load_image(path: list) -> pg.Surface:  # All images stored in data/
    cwd = os.path.dirname(__file__)
    img = pg.image.load(os.path.join(cwd, "data", *path))
    sfc = pg.Surface(img.get_size(), flags=pg.SRCALPHA)
    sfc.blit(img, (0, 0))
    return sfc


# Convert chipmunk coords to pymunk coords, flipping and offsetting y-coordinate
def flipy(point):
    return Vec2d(point[0], const.SCREEN_HEIGHT - point[1])


def invert_y(points):
    return [(x, -y) for x, y in points]


def rand_pos(sprite, rng):
    x = rng.randint(100, const.SCREEN_WIDTH - 100)
    if sprite == "banker":
        return x, rng.randint(170, 300)
    elif sprite == "prospector":
        return x, rng.randint(350, const.SCREEN_HEIGHT - (const.WATER_HEIGHT + 30))


def normalize_angle(angle):
    if angle > const.TWO_PI:
        return angle - const.TWO_PI
    elif angle < 0.0:
        return angle + const.TWO_PI
    return angle
