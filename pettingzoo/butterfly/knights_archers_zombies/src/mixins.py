"""Mix-in classes for other objects."""

import numpy as np
import numpy.typing as npt
import pygame

import pettingzoo.butterfly.knights_archers_zombies.src.constants as const


class VectorObservable:
    """Class to provide vector states.

    This adds two properties is for the knights-archers-zombies vector state:
    * vector_state
    * typemasked_vector_state

    Classes should implement direction, typemask, rect for
    these to be correct.
    """

    direction = pygame.Vector2(0, 0)
    typemask = [0, 0, 0, 0, 0, 0]
    rect: pygame.Rect

    @property
    def vector_state(self) -> npt.NDArray[np.float64]:
        """Return the vector observation for the Player."""
        return np.array(
            [
                self.rect.x / const.SCREEN_WIDTH,
                self.rect.y / const.SCREEN_HEIGHT,
                *self.direction,
            ]
        )

    @property
    def typemasked_vector_state(self) -> npt.NDArray[np.float64]:
        """Return the vector observation - with typemask."""
        return np.array(
            [
                *self.typemask,
                self.rect.x / const.SCREEN_WIDTH,
                self.rect.y / const.SCREEN_HEIGHT,
                *self.direction,
            ]
        )

    def get_vector_state(self, use_typemask: bool) -> npt.NDArray[np.float64]:
        """Return the vector observation with or without typemask."""
        if use_typemask:
            return self.typemasked_vector_state
        return self.vector_state
