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
        self.rects = [self.surf.get_rect()]
        self._speed = speed

    def reset(self, area: pygame.Rect, speed: float) -> None:
        """Resets the speed and location for a new game."""
        self._speed = speed
        if self._side == PaddleLocation.PADDLE_LEFT:
            self.rects[0].midleft = area.midleft
        else:
            self.rects[0].midright = area.midright

    def draw(self, screen):
        for rect in self.rects:
            pygame.draw.rect(screen, (255, 255, 255), rect)

    def update(self, area, action) -> None:
        # action: 0 - do nothing, 1 - up, 2 - down
        if action == 0:
            return
        movepos = [0, 0]
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

        Args:
            b_rect : Ball rect
            dx, dy : Ball speed along single axis
            b_speed : Ball speed

        Returns:
            is_collision: 1 if ball collides with paddle
            b_rect: new ball rect
            b_speed: new ball speed

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
            if b_speed[1] > 0:
                b_speed[1] *= -1
        # handle collision from bottom
        elif (
            b_rect.top < rect.bottom
            and b_rect.bottom - b_speed[1] > rect.bottom
            and b_speed[1] < 0
        ):
            b_rect.top = rect.bottom - 1
            if b_speed[1] < 0:
                b_speed[1] *= -1
        return True, b_rect, b_speed
