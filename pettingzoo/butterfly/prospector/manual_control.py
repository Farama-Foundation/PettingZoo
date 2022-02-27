import os

import numpy as np
import pygame

from . import constants as const


def manual_control(**kwargs):
    from .prospector import env as _env

    env = _env(**kwargs)
    clock = pygame.time.Clock()
    env.reset()
    default_scalar = 1
    agent = 0
    done = False
    quit_while = False

    while not done:
        clock.tick(const.FPS)
        agent_actions = (
            [np.array([0, 0, 0], dtype=np.float32) for _ in range(const.NUM_PROSPECTORS)]
            + [np.array([0, 0], dtype=np.float32) for _ in range(const.NUM_BANKERS)]
        )
        for event in pygame.event.get():
            # Use left/right arrow keys to switch between agents
            # Use WASD to control bankers
            # Use WASD and QE to control prospectors
            # Note: QE while selecting a banker has no effect.
            if event.type == pygame.KEYDOWN:
                # Agent selection
                if event.key == pygame.K_LEFT:
                    agent = (agent - 1) % const.NUM_AGENTS
                elif event.key == pygame.K_RIGHT:
                    agent = (agent + 1) % const.NUM_AGENTS
                # Forward/backward or up/down movement
                elif event.key == pygame.K_w:
                    agent_actions[agent][0] = default_scalar
                elif event.key == pygame.K_s:
                    agent_actions[agent][0] = -default_scalar
                # left/right movement
                elif event.key == pygame.K_a:
                    agent_actions[agent][1] = -default_scalar
                elif event.key == pygame.K_d:
                    agent_actions[agent][1] = default_scalar
                # rotation
                elif event.key == pygame.K_q:
                    if 0 <= agent <= 3:
                        agent_actions[agent][2] = default_scalar
                elif event.key == pygame.K_e:
                    if 0 <= agent <= 3:
                        agent_actions[agent][2] = -default_scalar
                elif event.key == pygame.K_ESCAPE:
                    done = True
                    quit_while = True
        if quit_while:
            break
        for a in agent_actions:
            env.step(a)
        env.render()

        done = any(env.dones.values())

    env.close()
