from os import path as os_path

import pygame


def get_image(path):
    cwd = os_path.dirname(os_path.dirname(__file__))
    image = pygame.image.load(cwd + "/" + path)
    sfc = pygame.Surface(image.get_size(), flags=pygame.SRCALPHA)
    sfc.blit(image, (0, 0))
    return sfc
