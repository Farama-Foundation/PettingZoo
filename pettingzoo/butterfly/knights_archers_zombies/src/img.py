import os

import pygame


def get_image(path):
    cwd = os.path.dirname(os.path.dirname(__file__))
    full_path = os.path.join(cwd, path)
    full_path = os.path.abspath(full_path)
    if os.path.commonpath([full_path, cwd]) != cwd:
        raise ValueError("Invalid path: path must be within the assets directory")
    image = pygame.image.load(full_path)
    sfc = pygame.Surface(image.get_size(), flags=pygame.SRCALPHA)
    sfc.blit(image, (0, 0))
    return sfc
