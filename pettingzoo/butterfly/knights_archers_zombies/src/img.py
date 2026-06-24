"""Utility to load images."""

from os import path as os_path

import pygame


def get_image(path: str) -> pygame.Surface:
    """Return a pygame surface loaded form the given path.

    Args:
        path: path relative to the directory containing this file
    """
    cwd = os_path.dirname(os_path.dirname(__file__))
    image = pygame.image.load(cwd + "/" + path)
    sfc = pygame.Surface(image.get_size(), flags=pygame.SRCALPHA)
    sfc.blit(image, (0, 0))
    return sfc
