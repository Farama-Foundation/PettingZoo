import piston_ball
import time
import numpy as np
import pygame

env = piston_ball.env()

i = 19

totalReward = 0

start = time.time()

done = False
quit_game = 0

pygame.key.set_repeat(20,0)

num_agents = env.num_agents # 20

while not done:
    actionList = np.array([0 for _ in range(num_agents)])
    for event in pygame.event.get():
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                quit_game = 1
                break
            if event.key == pygame.K_BACKSPACE:
                # Backspace to reset
                env.reset()
                i = 19
                totalReward = 0
            if event.key == pygame.K_a and time.time()-start > .1:
                i = (i-1) if (i != 0) else i
                start = time.time()
            if event.key == pygame.K_d and time.time()-start > .1:
                i = (i+1) if (i != num_agents-1) else i
                start = time.time()
            if event.key == pygame.K_s:
                actionList[i] = -1
            if event.key == pygame.K_w:
                actionList[i] = 1

    if quit_game:
        break
    # actions should be a dict of numpy arrays: {0: array([0,1,0])}
    action_dict = dict(zip(env.agent_ids, [np.array([0,0,0]) for _ in range(num_agents)])) # no action = [0,1,0]
    for idx, val in enumerate(actionList):
        action_dict[idx][val+1] = 1

    observations, reward, done, info = env.step(action_dict)
    env.render()
    totalReward += reward[0]
    done = done[0]

print("Total final reward is ", totalReward)
# Uncomment next line to print FPS at which the game runs
# print("fps = ", env.clock.get_fps())
env.close()
