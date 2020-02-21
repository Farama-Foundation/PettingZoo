from .prison import env as _env
import pygame
import numpy as np

env = _env(continuous=True, vector_observation=False)

x = 0
y = 0
while True:
    agent_actions = np.array([0 for _ in range(8)])
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
                agent_actions[env.convert_coord_to_prisoner_id((x, y))] = -20
            elif event.key == pygame.K_k:
                agent_actions[env.convert_coord_to_prisoner_id((x, y))] = 20

    actions = dict(zip(env.agent_list, agent_actions))
    obs, reward, done, info = env.step(actions)
    env.render()

    if True in list(done.values()):
        surfdemo_show(obs[1], "bs")
        break
