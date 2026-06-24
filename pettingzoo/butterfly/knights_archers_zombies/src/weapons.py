"""Weapons for the KAZ game."""

import os
from typing import TYPE_CHECKING

import pygame

from pettingzoo.butterfly.knights_archers_zombies.src import constants as const
from pettingzoo.butterfly.knights_archers_zombies.src.img import get_image
from pettingzoo.butterfly.knights_archers_zombies.src.mixins import VectorObservable

if TYPE_CHECKING:
    from pettingzoo.butterfly.knights_archers_zombies.src.players import (
        Archer,
        Knight,
        Player,
    )


class Weapon(pygame.sprite.Sprite, VectorObservable):
    """Base class for a weapon."""

    def __init__(self, player: "Player", image_name: str) -> None:
        """Initialize a weapon.

        Args:
            player: The player the weapon is from
            image_name: The filename of the image to render.
        """
        super().__init__()
        self.player = player
        self.image = get_image(os.path.join("img", image_name))
        self.rect = self.image.get_rect(center=self.player.rect.center)
        self.direction = self.player.direction


class Arrow(Weapon):
    """An arrow fired by an archer."""

    def __init__(self, archer: "Archer") -> None:
        """Initialize an Arrow fired by the given archer."""
        super().__init__(archer, "arrow.png")

        # rotate the arrow to align with archer who fired it
        angle = self.player.direction.angle_to(pygame.Vector2(0, -1))
        self.image = pygame.transform.rotate(self.image, angle)

        self.typemask = [0, 0, 0, 0, 1, 0]

    def act(self) -> None:
        """Move the arrow along its path."""
        self.rect.center = (
            int(self.rect.center[0] + self.direction[0] * const.ARROW_SPEED),
            int(self.rect.center[1] + self.direction[1] * const.ARROW_SPEED),
        )

    @property
    def is_active(self) -> bool:
        """Return True if the arrow is active.

        'Active' for an arrow means it is on the screen.
        """
        if self.rect.x < 0 or self.rect.y < 0:
            return False
        if self.rect.x > const.SCREEN_WIDTH or self.rect.y > const.SCREEN_HEIGHT:
            return False
        return True


class Sword(Weapon):
    """A sword carried by a knight.

    The 'sword' is actually rendered as a mace, but it is referred to as
    a sword everywhere.
    """

    def __init__(self, knight: "Knight") -> None:
        """Initialize the sword object for the given knight."""
        super().__init__(knight, "mace.png")
        self.knight = self.player
        self.active = True

        # arc of the sword, starts at the left most part
        self.arc = const.MAX_ARC

        self.typemask = [0, 0, 0, 1, 0, 0]

    def act(self) -> None:
        """Move the sword along its path."""
        # arc goes from max to min because it counts positive from CCW
        if self.arc > const.MIN_ARC:
            self.arc -= const.SWORD_SPEED

            new_dir = self.knight.direction.rotate(self.arc)
            self.rect = self.image.get_rect(center=self.knight.rect.center)
            self.rect.x += int(
                new_dir[0] * (self.rect.width + self.knight.rect.width) / 2
            )
            self.rect.y += int(
                new_dir[1] * (self.rect.height + self.knight.rect.height) / 2
            )
        else:
            self.active = False

    @property
    def is_active(self) -> bool:
        """Return True if the sword is still active."""
        return self.active
