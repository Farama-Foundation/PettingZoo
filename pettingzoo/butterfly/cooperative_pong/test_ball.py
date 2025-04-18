"""Test that Ball behaves correctly."""

import pygame
from gymnasium.utils import seeding

from pettingzoo.butterfly.cooperative_pong.ball import Ball
from pettingzoo.butterfly.cooperative_pong.cooperative_pong import get_valid_angle
from pettingzoo.butterfly.cooperative_pong.paddle import Paddle


def test_bounds() -> None:
    """Run multiple ball trajectories to confirm bounce works correctly."""

    # make ball size, screen size, ball speed match env default
    render_ratio = 2
    width, height = 960 // render_ratio, 560 // render_ratio
    ball_dims = (20 // render_ratio, 20 // render_ratio)
    ball_speed = 9

    area = pygame.Rect((0, 0, width, height))
    p0 = Paddle((4, 4), 0)
    p1 = Paddle((4, 4), 0)

    n_tests = 10000
    for seed in range(n_tests):
        randomizer, seed = seeding.np_random(seed=seed)
        ball = Ball(randomizer, ball_dims, ball_speed, bounce_randomness=False)

        ball.reset(area.center, get_valid_angle(randomizer))

        while True:
            ball.update2(area, p0, p1)
            terminate = ball.is_out_of_bounds()

            in_bounds = ball.rect.x >= 0 and ball.rect.x <= width - ball_dims[1]
            if not terminate and not in_bounds:
                assert (
                    False
                ), f"Cooperative pong not terminated with ball out of bounds (seed = {seed})"
            if terminate:
                break


if __name__ == "__main__":
    test_bounds()
