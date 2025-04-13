"""Contains utility functions used by several rlcard envs."""

import os
from typing import Any

import numpy as np
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


def calculate_width(
    possible_agents_list: list[Any],
    screen_width: int,
    i: int,
    tile_size: int,
    tile_scale: int = 31,
) -> int:
    """Calculate the width to use in rendering."""
    return int(
        (
            screen_width
            / (np.ceil(len(possible_agents_list) / 2) + 1)
            * np.ceil((i + 1) / 2)
        )
        + (tile_size * tile_scale / 616)
    )


def calculate_offset(hand: list[Any], j: int, tile_size: int) -> int:
    """Calculate the offset to use in rendering."""
    return int((len(hand) * (tile_size * 23 / 56)) - ((j) * (tile_size * 23 / 28)))


def calculate_height(
    screen_height: int, divisor: int, multiplier: int, tile_size: int, offset: float
) -> int:
    """Calculate the height to use in rendering."""
    return int(multiplier * screen_height / divisor + tile_size * offset)
