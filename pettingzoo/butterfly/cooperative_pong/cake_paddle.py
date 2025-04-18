import pygame

from pettingzoo.butterfly.cooperative_pong.paddle import Paddle, PaddleLocation


class CakePaddle(Paddle):
    def __init__(self, dims, speed, location):
        super().__init__(dims, speed, location)

        if self._side == PaddleLocation.PADDLE_LEFT:
            raise ValueError("CakePaddle does not support left paddle")

        # add remaining parts of the paddle
        # rects[0] is on the right, they go to the left as index increase
        dims2 = dims[0], dims[1] * 2 // 3
        dims3 = dims[0], dims[1] * 1 // 3
        dims4 = dims[0], dims[1] // 12
        self.rects.append(pygame.Rect((0, 0), dims2))
        self.rects.append(pygame.Rect((0, 0), dims3))
        self.rects.append(pygame.Rect((0, 0), dims4))

    def reset(self, area: pygame.Rect, speed: float) -> None:
        """Resets the speed and location for a new game."""
        super().reset(area, speed)
        # move the rest of the paddle parts to stay lined up
        self.rects[1].midright = self.rects[0].midleft
        self.rects[2].midright = self.rects[1].midleft
        self.rects[3].midright = self.rects[2].midleft
