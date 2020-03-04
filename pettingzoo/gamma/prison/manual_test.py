from .prison import env as _env
import pygame
import numpy as np

def manual_control(**kwargs):
    env = _env(**kwargs)
    x = 0
    y = 0
    while True:
        agent_actions = np.array([0 for _ in range(8)])
        num_actions = 0
        for event in pygame.event.get():
            # wasd to switch prisoner, jk to move left and right
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_a:
                    x = 0
                elif event.key == pygame.K_d:
                    x = 1
                elif event.key == pygame.K_w:
                    y = max(0, y-1)
                elif event.key == pygame.K_s:
                    y = min(3, y+1)
                elif event.key == pygame.K_j:
                    num_actions += 1
                    agent_actions[env.convert_coord_to_prisoner_id((x, y))] = -20
                elif event.key == pygame.K_k:
                    num_actions += 1
                    agent_actions[env.convert_coord_to_prisoner_id((x, y))] = 20

        actions = dict(zip(env.agents, agent_actions))
        test_done = False
        for i in env.agents:
            reward, done, info = env.last_cycle()
            if done:
                test_done = True
            action = actions[i]
            obs = env.step(action)
        env.render()

        if test_done:
            break
    env.close()

if __name__ == "__main__":
    manual_control()

