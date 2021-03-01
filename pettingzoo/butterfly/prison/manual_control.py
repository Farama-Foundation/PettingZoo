import os
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = 'hide'
import pygame
import numpy as np


def manual_control(**kwargs):
    from .prison import env as _env
    env = _env(**kwargs)
    env.reset()
    clock = pygame.time.Clock()
    x = 0
    y = 0
    prisoner_mapping = {}
    for prisoner in env.agents:
        prisoner_mapping[env.infos[prisoner]['map_tuple']] = prisoner
    while True:
        clock.tick(30)
        agent_actions = {agent: 1 for agent in env.agents}
        num_actions = 0
        test_done = False
        for event in pygame.event.get():
            # wasd to switch prisoner, jk to move left and right
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_a:
                    x = 0
                elif event.key == pygame.K_d:
                    x = 1
                elif event.key == pygame.K_w:
                    y = max(0, y - 1)
                elif event.key == pygame.K_s:
                    y = min(3, y + 1)
                elif event.key == pygame.K_j:
                    num_actions += 1
                    agent_actions[prisoner_mapping[
                        (x, y)]] = 0
                elif event.key == pygame.K_k:
                    num_actions += 1
                    agent_actions[prisoner_mapping[
                        (x, y)]] = 2
                elif event.key == pygame.K_ESCAPE:
                    test_done = True
        for i in env.agents:
            observation, reward, done, info = env.last()
            # if reward != 0:
            #     print("Agent {} was reward {}".format(i, reward))
            if done:
                test_done = True
            action = agent_actions[i]
            env.step(action)
        env.render()

        if test_done:
            break
    env.close()


if __name__ == "__main__":
    manual_control()
