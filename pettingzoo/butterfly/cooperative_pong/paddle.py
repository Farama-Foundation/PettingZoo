from enum import Enum

import pygame


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
    def __init__(self, dims, speed, location):
        self._side = paddle_location_mapping[location]
        self.surf = pygame.Surface(dims)
        self.rect = self.surf.get_rect()
        self.speed = speed

    def reset(self):
        pass

    def draw(self, screen):
        pygame.draw.rect(screen, (255, 255, 255), self.rect)

    def update(self, area, action):
        # action: 1 - up, 2 - down
        movepos = [0, 0]
        if action > 0:
            if action == 1:
                movepos[1] = movepos[1] - self.speed
            elif action == 2:
                movepos[1] = movepos[1] + self.speed

            # make sure the players stay inside the screen
            newpos = self.rect.move(movepos)
            if area.contains(newpos):
                self.rect = newpos

    def process_collision(self, b_rect, b_speed):
        """Process a collision.

        Args:
            b_rect : Ball rect
            dx, dy : Ball speed along single axis
            b_speed : Ball speed

        Returns:
            is_collision: 1 if ball collides with paddle
            b_rect: new ball rect
            b_speed: new ball speed

        """
        if not self.rect.colliderect(b_rect):
            return False, b_rect, b_speed
        # handle collision from left or right
        if self._side == PaddleLocation.PADDLE_LEFT and b_rect.left < self.rect.right:
            b_rect.left = self.rect.right
            if b_speed[0] < 0:
                b_speed[0] *= -1
        elif (
            self._side == PaddleLocation.PADDLE_RIGHT and b_rect.right > self.rect.left
        ):
            b_rect.right = self.rect.left
            if b_speed[0] > 0:
                b_speed[0] *= -1
        # handle collision from top
        if (
            b_rect.bottom > self.rect.top
            and b_rect.top - b_speed[1] < self.rect.top
            and b_speed[1] > 0
        ):
            b_rect.bottom = self.rect.top
            if b_speed[1] > 0:
                b_speed[1] *= -1
        # handle collision from bottom
        elif (
            b_rect.top < self.rect.bottom
            and b_rect.bottom - b_speed[1] > self.rect.bottom
            and b_speed[1] < 0
        ):
            b_rect.top = self.rect.bottom - 1
            if b_speed[1] < 0:
                b_speed[1] *= -1
        return True, b_rect, b_speed
