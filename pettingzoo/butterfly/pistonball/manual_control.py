import os
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = 'hide'
import time
import numpy as np
import pygame


def manual_control(**kwargs):
    from .pistonball import env as _env

    # flatten_obs is True by default
    env = _env(**kwargs)
    env.reset()
    # Use save_observation to save a dictionary of observations
    # save_observation(obs_dict, reverse_colors=False)
    # exit()
    i = 19
    clock = pygame.time.Clock()
    start = time.time()
    done = False
    quit_game = 0
    pygame.key.set_repeat(20, 0)
    num_agents = len(env.agents)  # 20
    while not done:
        clock.tick(60)
        action_list = np.array([1 for _ in range(num_agents)])
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    quit_game = 1
                    break
                if event.key == pygame.K_BACKSPACE:
                    # Backspace to reset
                    env.reset()
                    i = 19
                if event.key == pygame.K_a and time.time() - start > .1:
                    i = (i - 1) if (i != 0) else i
                    start = time.time()
                if event.key == pygame.K_d and time.time() - start > .1:
                    i = (i + 1) if (i != num_agents - 1) else i
                    start = time.time()
                if event.key == pygame.K_s:
                    action_list[i] = 0
                if event.key == pygame.K_w:
                    action_list[i] = 2

        if quit_game:
            break
        # actions should be a dict of numpy arrays
        for a in action_list:
            env.step(a)
            pygame.event.pump()

        env.render()
        done = any(env.dones.values())
    # Uncomment next line to print FPS at which the game runs

    env.close()
