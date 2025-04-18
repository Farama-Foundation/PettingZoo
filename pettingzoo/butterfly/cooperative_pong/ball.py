import numpy as np
import pygame


def get_small_random_value(randomizer):
    # generates a small random value between [0, 1/100)
    return (1 / 100) * randomizer.random()


class Ball(pygame.sprite.Sprite):
    def __init__(self, randomizer, dims, speed, bounce_randomness=False):
        self.surf = pygame.Surface(dims)
        self.rect = self.surf.get_rect()
        self.speed_val = speed
        self.speed = [
            int(self.speed_val * np.cos(np.pi / 4)),
            int(self.speed_val * np.sin(np.pi / 4)),
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
            int(self.speed_val * np.cos(angle)),
            int(self.speed_val * np.sin(angle)),
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

        # Do ball and bat collide?
        # add some randomness
        r_val = 0
        if self.bounce_randomness:
            r_val = get_small_random_value(self.randomizer)

        # ball in left half of screen
        if self.rect.center[0] < area.center[0]:
            is_collision, self.rect, self.speed = p0.process_collision(
                self.rect, self.speed, 1
            )
            if is_collision:
                self.speed = [
                    self.speed[0] + np.sign(self.speed[0]) * r_val,
                    self.speed[1] + np.sign(self.speed[1]) * r_val,
                ]
        # ball in right half
        else:
            is_collision, self.rect, self.speed = p1.process_collision(
                self.rect, self.speed, 2
            )
            if is_collision:
                self.speed = [
                    self.speed[0] + np.sign(self.speed[0]) * r_val,
                    self.speed[1] + np.sign(self.speed[1]) * r_val,
                ]

    def draw(self, screen):
        # screen.blit(self.surf, self.rect)
        pygame.draw.rect(screen, (255, 255, 255), self.rect)
