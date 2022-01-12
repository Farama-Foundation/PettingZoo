import os
import time

import numpy as np
import pygame


def manual_control(**kwargs):
    from .pursuit import env as _env

    x_size = 5
    y_size = 5
    obs_range = 3
    n_evaders = 1
    n_pursuers = 2

    clock = pygame.time.Clock()

    # obs_range should be odd 3, 5, 7, etc
    env = _env(
        n_pursuers=n_pursuers, n_evaders=n_evaders, x_size=x_size, y_size=y_size, obs_range=obs_range
    )

    env.reset()

    done = False

    global _quit_loop, _actions, _agent_id
    _quit_loop = np.array([0])
    _actions = np.array([4] * env.num_agents)
    _agent_id = np.array([0])

    done = False
    num_frames = 0
    total_reward = 0

    while not done:
        clock.tick(15)
        num_frames += 1
        env.render()
        if _quit_loop[0]:
            break
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_j:
                    # pressing 'j' moves the focus of control to the next agent
                    # control rolls over to the first agent
                    _agent_id[0] = (_agent_id[0] + 1) % env.num_agents
                elif event.key == pygame.K_k:
                    # pressing 'k' moves the focus of control to the previous agent
                    # control rolls over to the lastagent
                    _agent_id[0] = (_agent_id[0] - 1) % env.num_agents
                elif event.key == pygame.K_UP:
                    # p1: up
                    _actions[_agent_id[0]] = 3
                elif event.key == pygame.K_DOWN:
                    # p1: down
                    _actions[_agent_id[0]] = 2
                elif event.key == pygame.K_LEFT:
                    # p1: left
                    _actions[_agent_id[0]] = 0
                elif event.key == pygame.K_RIGHT:
                    # p1: right
                    _actions[_agent_id[0]] = 1
                elif event.key == pygame.K_BACKSPACE:
                    env.reset()
                elif event.key == pygame.K_ESCAPE:
                    _quit_loop[0] = 1
                    # break
        # actions should be a dict of numpy arrays
        for a in _actions:
            obs, reward, d, info = env.last()
            env.step(a)
            pygame.event.pump()
            if d:
                done = True
            total_reward += reward

        _actions = np.array([4] * env.num_agents)

    env.render()
    time.sleep(2)
    env.close()
