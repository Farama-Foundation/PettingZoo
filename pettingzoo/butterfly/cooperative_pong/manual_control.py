import os

import numpy as np
import pygame


def manual_control(**kwargs):
    from .cooperative_pong import env as _env
    env = _env(**kwargs)
    env.reset()

    quit_loop = 0

    pygame.key.set_repeat(20, 0)
    clock = pygame.time.Clock()

    total_reward = 0
    initial_iteration = {agent: True for agent in env.agents}
    dones = {agent: False for agent in env.agents}
    done = all(dones.values())

    while not done:
        clock.tick(15)
        action_dict = {agent: 0 for agent in env.agents}  # do nothing
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                quit_loop = 1
                break
            elif event.type == pygame.KEYDOWN:
                # Quit if ESC is pressed
                if event.key == pygame.K_ESCAPE:
                    quit_loop = 1
                    break
                if event.key == pygame.K_BACKSPACE:
                    env.reset()
                    total_reward = 0
                if event.key == pygame.K_w:
                    # player1.moveup()
                    action_dict[env.agents[0]] = 1
                if event.key == pygame.K_s:
                    # player1.movedown()
                    action_dict[env.agents[0]] = 2
                if event.key == pygame.K_UP:
                    # player2.moveup()
                    action_dict[env.agents[1]] = 1
                if event.key == pygame.K_DOWN:
                    # player2.movedown()
                    action_dict[env.agents[1]] = 2
        if quit_loop:
            break

        for _ in env.agents:
            agent = env.agent_selection
            obs, reward, dones[agent], _ = env.last()
            total_reward += reward
            initial_iteration[agent] = False
            env.step(action_dict[agent])
        done = all(env.dones.values())

        env.render()
        pygame.event.pump()

    env.close()
