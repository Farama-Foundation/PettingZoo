import pygame
import numpy as np


def manual_control(**kwargs):
    from .prison import env as _env
    env = _env(**kwargs)
    env.reset()
    x = 0
    y = 0
    while True:
        agent_actions = np.array([1 for _ in range(8)])
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
                    agent_actions[env.convert_coord_to_prisoner_id(
                        (x, y))] = 0
                elif event.key == pygame.K_k:
                    num_actions += 1
                    agent_actions[env.convert_coord_to_prisoner_id(
                        (x, y))] = 2
                elif event.key == pygame.K_ESCAPE:
                    test_done = True

        actions = dict(zip(env.agents, agent_actions))
        for i in env.agents:
            reward, done, info = env.last()
            if reward != 0:
                print("Agent {} was reward {}".format(i, reward))
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
