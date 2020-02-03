# from .game import env as _env
import game
import time
import numpy as np
import pygame
import random

if __name__ == "__main__":
    env = game.env()
    done = False

    start_time = time.time()
    frame_count = 0
    frame_limit = 500
    quit_game = 0

    # while not done:
    while frame_count < frame_limit:
        frame_count += 1
        actions = [random.randint(1, 5) for x in range(env.num_agents)]

        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    quit_game = 1
                    break
                if event.key == pygame.K_BACKSPACE:
                    # Backspace to reset
                    env.reset()
                    # totalReward = 0

        if quit_game:
            break

        observations, reward_dict, done_dict, info = env.step(actions)
        # env.render()
        # env.plot_obs(observations, "obs")
        done = done_dict['__all__']
        # quit()

    print('FPS:', frame_count / (time.time() - start_time))