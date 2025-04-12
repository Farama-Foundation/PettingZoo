"""Contains utility functions used by several rlcard envs."""

import os

import pygame


def _get_full_path(path: str) -> str:
    """Return the path as the given path in this file's directory."""
    cwd = os.path.dirname(__file__)
    full_path = os.path.join(cwd, path)
    return full_path


def get_image(path: str) -> pygame.Surface:
    """Return an image from the given path."""
    full_path = _get_full_path(path)
    image = pygame.image.load(full_path)
    return image


def get_font(path: str, size: int) -> pygame.font.Font:
    """Return a font from the given path."""
    full_path = _get_full_path(path)
    font = pygame.font.Font(full_path, size)
    return font
