"""A flat paddle."""

from enum import Enum
from typing import Literal

import pygame

ActionType = Literal[0, 1, 2]


class PaddleLocation(Enum):
    """The location of the paddle."""

    PADDLE_LEFT = 1
    PADDLE_RIGHT = 2


# map side to an index
paddle_location_mapping = {
    "left": PaddleLocation.PADDLE_LEFT,
    "right": PaddleLocation.PADDLE_RIGHT,
}


class Paddle(pygame.sprite.Sprite):
    """A flat paddle for the pong game."""

    def __init__(
        self, dims: tuple[int, int], speed: float, location: Literal["left", "right"]
    ) -> None:
        """Initialize the Paddle object.

        The paddle needs to be placed in the proper location by calling
        reset() prior to use.

        Args:
            dims: the dimensions of the paddle.
            speed: the speed the paddle will move at
            location: the location of the paddle, either "left" or "right"
        """
        self._side = paddle_location_mapping[location]
        self.rects = [pygame.Rect((0, 0), dims)]
        self._speed = speed

    def reset(self, area: pygame.Rect, speed: float) -> None:
        """Resets the speed and location for a new game.

        The paddle is placed on the proper edge of the given
        area, centered vertically. The speed is set to the
        given value.

        Args:
            area: the screen to place the paddle in
            speed: the new speed of the paddle
        """
        self._speed = speed
        if self._side == PaddleLocation.PADDLE_LEFT:
            self.rects[0].midleft = area.midleft
        else:
            self.rects[0].midright = area.midright

    def draw(self, screen: pygame.Surface) -> None:
        """Draw the paddle on the given screen."""
        for rect in self.rects:
            pygame.draw.rect(screen, (255, 255, 255), rect)

    def update(self, area: pygame.Rect, action: ActionType) -> None:
        """Apply the given action and update the paddle position.

        Valid actions are:
            0 - do nothing
            1 - move paddle up
            2 - move paddle down

        The paddle is moved a distance equal to its speed (defined either
        on creation or during reset()). If moving the paddle up or down
        would result in it leaving the screen, no movement is done.

        Args:
            area: the Rect of the screen to move in
            action: the action to take
        """
        if action == 0:
            return
        movepos = [0.0, 0.0]
        if action == 1:
            movepos[1] = -self._speed
        elif action == 2:
            movepos[1] = self._speed

        # make sure the players stay inside the screen
        newpos = self.rects[0].move(movepos)
        if area.contains(newpos):
            for rect in self.rects:
                rect.move_ip(movepos)

    def process_collision(
        self, b_rect: pygame.Rect, b_speed: list[float]
    ) -> tuple[bool, pygame.Rect, list[float]]:
        """Process a collision.

        If a collision happens, a new speed and position rect
        will be returned. If there is no collision, the speed
        and rect are returned unchanged.

        Args:
            b_rect: the ball's Rect object, giving its position
            b_speed: the ball's x,y speed components

        Returns:
            A tuple giving the following:
              True if the ball collided with paddle
              the ball's new Rect object, giving its position
              the ball's new x,y speed components
        """
        # this is reversed to work properly for the subclass CakePaddle
        # where rects are the end are in front of rects at the beginning
        for rect in reversed(self.rects):
            if rect.colliderect(b_rect):
                return self._process_collision_with_rect(rect, b_rect, b_speed)

        # report no collisions found
        return False, b_rect, b_speed

    def _process_collision_with_rect(
        self, rect: pygame.Rect, b_rect: pygame.Rect, b_speed: list[float]
    ) -> tuple[bool, pygame.Rect, list[float]]:
        """Apply a collision with part of the paddle.

        A new speed and position of the ball is calculated based on the details
        of the collision.

        Args:
            rect: the rect for the part of the paddle to check
            b_rect: the ball's Rect object, giving its position
            b_speed: the ball's x,y speed components

        Returns:
            A tuple giving the following:
              True if the ball collided with the rect
              the ball's new Rect object, giving its position
              the ball's new x,y speed components
        """
        # handle collision from left or right
        if self._side == PaddleLocation.PADDLE_LEFT and b_rect.left < rect.right:
            b_rect.left = rect.right
            if b_speed[0] < 0:
                b_speed[0] *= -1
        elif self._side == PaddleLocation.PADDLE_RIGHT and b_rect.right > rect.left:
            b_rect.right = rect.left
            if b_speed[0] > 0:
                b_speed[0] *= -1
        # handle collision from top
        if (
            b_rect.bottom > rect.top
            and b_rect.top - b_speed[1] < rect.top
            and b_speed[1] > 0
        ):
            b_rect.bottom = rect.top
            b_speed[1] *= -1
        # handle collision from bottom
        elif (
            b_rect.top < rect.bottom
            and b_rect.bottom - b_speed[1] > rect.bottom
            and b_speed[1] < 0
        ):
            b_rect.top = rect.bottom - 1
            b_speed[1] *= -1
        return True, b_rect, b_speed
