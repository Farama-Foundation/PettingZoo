"""Zombie object for Knights-Archers-Zombies."""
import os

import numpy as np
import pygame

from pettingzoo.butterfly.knights_archers_zombies.src import constants as const
from pettingzoo.butterfly.knights_archers_zombies.src.img import get_image
from pettingzoo.butterfly.knights_archers_zombies.src.interval import Interval
from pettingzoo.butterfly.knights_archers_zombies.src.mixins import VectorObservable


class Zombie(pygame.sprite.Sprite, VectorObservable):
    """A zombie for the Knight-Archers-Zombie game."""

    # this is the valid range of x values allowed. It corresponds to the
    # visible region on the screen that is between the two walls.
    x_range: list[int] = [const.WALL_WIDTH, const.SCREEN_WIDTH - const.WALL_WIDTH]

    def __init__(self, randomizer: np.random.Generator) -> None:
        """Initialize the Zombie agent.

        Args:
            randomizer: the random generator to use in placing/moving the zombie
        """
        super().__init__()
        self.image = get_image(os.path.join("img", "zombie.png"))
        self.rect = self.image.get_rect(center=(50, 50))

        # move rect to random starting position at the top
        self.rect.y = 5
        low_x, high_x = self.x_range
        self.rect.x = int(randomizer.integers(low_x, high_x))

        self.wobble_interval = Interval(3)
        self.randomizer = randomizer
        self.direction = pygame.Vector2(0, 1)
        self.typemask = [1, 0, 0, 0, 0, 0]

    def act(self) -> None:
        """Move the zombie.

        The zombie always moves down the screen. Sometimes it will also move
        left or right. In all cases, it will stay within the left/right walls.
        """
        self.rect.y += const.ZOMBIE_Y_SPEED

        # Wobbling in X Direction. he original code seemed to have this every
        # 3 steps. Not sure why that was chosen, but the behavior has been
        # retained here. On these steps, there *may* be some left/right movement.
        # On other steps, there is only downward movement.
        if self.wobble_interval.increment():
            # The random left/right motion is determined from this random value:
            #   values of 0, 7, 9 result in no movement left or right
            #   values of 1, 3, 6 result in movement to the right
            #   values of 2, 4, 5, 8 result in movement to the left
            # I have no idea why it was set up this way, but that behavior has
            # been preserved.
            # Movement that would take the zombie through a left/right wall
            # is rejected, leading to no left right motion in these cases.
            rand_x = self.randomizer.integers(0, 10)
            proposed_x = self.rect.x
            if rand_x in [1, 3, 6]:
                proposed_x += const.ZOMBIE_X_SPEED
            elif rand_x in [2, 4, 5, 8]:
                proposed_x -= const.ZOMBIE_X_SPEED

            if self.x_range[0] <= proposed_x <= self.x_range[1]:
                self.rect.x = proposed_x
