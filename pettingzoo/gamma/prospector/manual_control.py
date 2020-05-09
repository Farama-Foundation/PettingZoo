import pygame
import numpy as np
from . import constants as const


def manual_control(**kwargs):
    from .prospector import env as _env

    env = _env(**kwargs)
    env.reset()
    default_scalar = 0.8

    while True:
        agent_actions = np.array(
            [[0, 0, 0] for _ in range(const.NUM_PROSPECTORS)]
            + [[0, 0, 0] for _ in range(const.NUM_BANKERS)]
        )
        num_actions = 0
        agent = 0
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
                    num_actions += 1
                    agent_actions[agent][0] = default_scalar
                elif event.key == pygame.K_s:
                    num_actions += 1
                    agent_actions[agent][0] = -default_scalar
                # left/right movement
                elif event.key == pygame.K_a:
                    num_actions += 1
                    agent_actions[agent][1] = -default_scalar
                elif event.key == pygame.K_d:
                    num_actions += 1
                    agent_actions[agent][1] = default_scalar
                # rotation
                elif event.key == pygame.K_q:
                    if 0 <= agent <= 3:
                        num_actions += 1
                        agent_actions[agent][2] = default_scalar
                elif event.key == pygame.K_e:
                    if 0 <= agent <= 3:
                        num_actions += 1
                        agent_actions[agent][2] = -default_scalar
                elif event.key == pygame.K_ESCAPE:
                    test_done = True
        actions = dict(zip(env.agents, agent_actions))
        test_done = False
        for i in env.agents:
            reward, done, info = env.last()
            if done:
                test_done = True
            action = actions[i]
            env.step(action, observe=False)
        env.render()

        if test_done:
            break
    env.close()


if __name__ == "__main__":
    manual_control()
