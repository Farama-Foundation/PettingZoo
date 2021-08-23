import os
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = 'hide'
import time
import pygame


def manual_control(**kwargs):
    from .knights_archers_zombies import env as _env
    env = _env(**kwargs)
    env.reset()
    done = False
    FPS = 90
    clock = pygame.time.Clock()

    cur_agent = 0
    frame_count = 0
    # frame_limit = 500
    quit_game = 0

    while not done:
        clock.tick(FPS)
        # while frame_count < frame_limit: # Uncomment this if you want the game to run for fame_limit amount of frames instead of ending by normal game conditions (useful for testing purposes)
        agents = env.agents
        frame_count += 1
        actions = [5 for x in range(len(env.agents))]  # If you want to do manual input
        # 5 is do nothing, 0 is up, 1 is down, 2 is turn CW, 3 is CCW, 4 is attack
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
                    actions[cur_agent] = 2
                if event.key == pygame.K_e:
                    actions[cur_agent] = 3
                if event.key == pygame.K_w:
                    actions[cur_agent] = 0
                if event.key == pygame.K_s:
                    actions[cur_agent] = 1
                if event.key == pygame.K_f:
                    actions[cur_agent] = 4

        if quit_game:
            break
        for a in actions:
            env.step(a)
        env.render()
        done = any(env.dones.values())

    env.close()
