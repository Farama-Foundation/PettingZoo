"""Ball for a Cooperative Pong game."""

import math

import numpy as np
import pygame

from pettingzoo.butterfly.cooperative_pong.paddle import Paddle


def get_small_random_value(randomizer: np.random.Generator) -> float:
    """Returns a random value in [-1/100, 1/100) from the given generator."""
    return 2 * (1 / 100.0) * randomizer.random() - (1 / 100.0)


def change_speed_angle(speed: list[float], delta_angle: float) -> list[float]:
    """Change angle, but not magnitude of speed.

    The takes an existing veloctiy and returns a new velocity with the
    direction changed but the magnitude the same.

    Args:
        speed: the speed in x,y coordinates
        delta_angle: change in angle to apply (in radians)

    Returns:
        A list with the new speed x,y components
    """
    magnitude = math.sqrt(speed[0] ** 2 + speed[1] ** 2)
    current_angle_rad = math.atan2(speed[1], speed[0])

    new_angle_rad = current_angle_rad + delta_angle

    new_x = magnitude * math.cos(new_angle_rad)
    new_y = magnitude * math.sin(new_angle_rad)

    return [new_x, new_y]


class Ball(pygame.sprite.Sprite):
    """The ball in a Cooperative Pong Game.

    If desired, the ball bounces off objects with a small randomness in angle.
    """

    def __init__(
        self,
        randomizer: np.random.Generator,
        dims: tuple[int, int],
        speed: float,
        bounce_randomness: bool = False,
    ) -> None:
        """Initializes a new Ball.

        The position defaults to (0,0) and should be set via reset() prior to
        being used.

        Args:
            randomizer: numpy randomizer to use for bounces
            dims: the size of the ball
            speed: the magnitude of the ball's speed
            bounce_randomness: whether to add speed randomness in bounces
        """
        self._surf = pygame.Surface(dims)
        self._surf.fill((255, 255, 255))
        self._rect = self._surf.get_rect()
        self._speed_val = speed
        self._speed = [
            self._speed_val * np.cos(np.pi / 4),
            self._speed_val * np.sin(np.pi / 4),
        ]
        self._bounce_randomness = bounce_randomness
        self._randomizer = randomizer
        self._out_of_bounds = False

    def reset(self, center: tuple[int, int], angle: float) -> None:
        """Reset speed and position of ball.

        The ball is centered on the given position and the direction of the
        ball's motion is set to the given angle.

        Args:
            center: the new center of the ball
            angle: the direction of ball's velocity (radians).
        """
        self._rect.center = center
        self._speed = [
            self._speed_val * np.cos(angle),
            self._speed_val * np.sin(angle),
        ]
        self._out_of_bounds = False

    def is_out_of_bounds(self) -> bool:
        """Return True if the ball is out of bounds."""
        return self._out_of_bounds

    def update2(self, area: pygame.Rect, p0: Paddle, p1: Paddle) -> None:
        """Update the ball position.

        The ball bounces off paddles and the top and bottom walls.
        If the ball exits left or right, it is marked as out of
        bounds.

        Args:
            area: The area of the screen
            p0: The left paddle
            p1: The right paddle
        """
        # move ball rect
        self._rect.x += self._speed[0]
        self._rect.y += self._speed[1]

        if not area.contains(self._rect):
            # bottom wall
            if self._rect.bottom > area.bottom:
                self._rect.bottom = area.bottom
                self._speed[1] = -self._speed[1]
            # top wall
            elif self._rect.top < area.top:
                self._rect.top = area.top
                self._speed[1] = -self._speed[1]

        # after bouncing back from the top/bottom, if it is still out of
        # bounds, it is because it went out the left or right. No need to
        # finish the update.
        if not area.contains(self._rect):
            self._out_of_bounds = True
            return None

        # Do ball and paddle collide?
        if self._rect.center[0] < area.center[0]:  # ball in left half of screen
            paddle = p0
        else:  # ball in right half
            paddle = p1
        is_collision, self._rect, self._speed = paddle.process_collision(
            self._rect, self._speed
        )

        # add randomness if there was a collision (if requested)
        if is_collision and self._bounce_randomness:
            delta_angle = get_small_random_value(self._randomizer)
            self._speed = change_speed_angle(self._speed, delta_angle)

        return None

    def draw(self, screen: pygame.Surface) -> None:
        """Draw the ball on the given surface."""
        screen.blit(self._surf, self._rect)
