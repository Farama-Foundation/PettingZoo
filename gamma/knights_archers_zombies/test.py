# from .game import env as _env
import game
import time
import numpy as np
import pygame
import random

if __name__ == "__main__":
    env = game.env(2,2)
    done = False

    cur_agent = 0

    start_time = time.time()
    frame_count = 0
    frame_limit = 500
    quit_game = 0

    while not done:
    # while frame_count < frame_limit: # Uncomment this if you want the game to run for fame_limit amount of frames instead of ending by normal game conditions (useful for testing purposes)
        agents = env.agent_list
        frame_count += 1
        # actions = [random.randint(1, 5) for x in range(env.num_agents)] # If you want to do random inputs
        actions = [6 for x in range(env.num_agents)] # If you want to do manual input

        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    quit_game = 1
                    break
                if event.key == pygame.K_BACKSPACE:
                    # Backspace to reset
                    env.reset()
                    # totalReward = 0
                if event.key == pygame.K_a:
                    cur_agent -= 1
                    if cur_agent < 0:
                        cur_agent = len(agents) - 1
                if event.key == pygame.K_d:
                    cur_agent += 1
                    if cur_agent > len(agents) - 1:
                        cur_agent = 0
                if event.key == pygame.K_q:
                    actions[cur_agent] = 3
                if event.key == pygame.K_e:
                    actions[cur_agent] = 4
                if event.key == pygame.K_w:
                    actions[cur_agent] = 1
                if event.key == pygame.K_s:
                    actions[cur_agent] = 2
                if event.key == pygame.K_f:
                    actions[cur_agent] = 5

        if quit_game:
            break

        observations, reward_dict, done_dict, info = env.step(actions)
        env.render()
        # env.plot_obs(observations, "obs")
        done = done_dict['__all__']
        # quit()

    end_time = time.time()
    total_time = end_time - start_time
    print('Totla time:', total_time)
    print('FPS:', frame_count / (total_time))
    print('============')
    for key in env.timer_dict:
        print('** {} **'.format(key))
        print('Avg seconds per frame: {}'.format(env.timer_dict[key] / frame_count))
        print('Percentage of runtime: {}%'.format((env.timer_dict[key] / total_time) * 100))
        print()