import math

import numpy as np
import pygame


def get_small_random_value(randomizer: np.random.Generator) -> float:
    """Returns a random value in [-1/100, 1/100) from the given generator."""
    return 2 * (1 / 100.0) * randomizer.random() - (1 / 100.0)


def change_speed_angle(
    speed: list[float, float], delta_angle: float
) -> list[float, float]:
    """Change angle, but not magnitude of speed.

    Args:
      speed: the speed in x,y coordinates
      delta_angle: change in angle to apply (in radians)

    Returns:
      the new speed in x,y coordinates
    """
    magnitude = math.sqrt(speed[0] ** 2 + speed[1] ** 2)
    current_angle_rad = math.atan2(speed[1], speed[0])

    new_angle_rad = current_angle_rad + delta_angle

    new_x = magnitude * math.cos(new_angle_rad)
    new_y = magnitude * math.sin(new_angle_rad)

    return [new_x, new_y]


class Ball(pygame.sprite.Sprite):
    def __init__(self, randomizer, dims, speed, bounce_randomness=False):
        self.surf = pygame.Surface(dims)
        self.surf.fill((255, 255, 255))
        self.rect = self.surf.get_rect()
        self.speed_val = speed
        self.speed = [
            self.speed_val * np.cos(np.pi / 4),
            self.speed_val * np.sin(np.pi / 4),
        ]
        self.bounce_randomness = bounce_randomness
        self.randomizer = randomizer
        self._out_of_bounds = False

    def reset(self, center: tuple[int, int], angle: float) -> None:
        """Reset speed and position of ball.

        The ball is centered on the given position and the direction of the
        ball's motion is set to the given angle.

        Args:
          center: the new center of the ball
          angle: the angle of the motion - used to set speed components.
        """
        self.rect.center = center
        self.speed = [
            self.speed_val * np.cos(angle),
            self.speed_val * np.sin(angle),
        ]
        self._out_of_bounds = False

    def is_out_of_bounds(self) -> bool:
        """Return True if the ball is out of bounds."""
        return self._out_of_bounds

    def update2(self, area, p0, p1):
        # move ball rect
        self.rect.x += self.speed[0]
        self.rect.y += self.speed[1]

        if not area.contains(self.rect):
            # bottom wall
            if self.rect.bottom > area.bottom:
                self.rect.bottom = area.bottom
                self.speed[1] = -self.speed[1]
            # top wall
            elif self.rect.top < area.top:
                self.rect.top = area.top
                self.speed[1] = -self.speed[1]

        # after bouncing back from the top/bottom, if it is still out of
        # bounds, it is because it went out the left or right. No need to
        # finish the update.
        if not area.contains(self.rect):
            self._out_of_bounds = True
            return None

        # Do ball and paddle collide?
        if self.rect.center[0] < area.center[0]:  # ball in left half of screen
            is_collision, self.rect, self.speed = p0.process_collision(
                self.rect, self.speed, 1
            )
        else:  # ball in right half
            is_collision, self.rect, self.speed = p1.process_collision(
                self.rect, self.speed, 2
            )

        # add randomness if there was a collision (if requested)
        if is_collision and self.bounce_randomness:
            delta_angle = get_small_random_value(self.randomizer)
            self.speed = change_speed_angle(self.speed, delta_angle)

    def draw(self, screen):
        screen.blit(self.surf, self.rect)
