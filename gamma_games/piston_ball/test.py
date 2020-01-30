import piston_ball
import time
import numpy as np
import pygame

env = piston_ball.env()
env.reset()

i = 19

totalReward = 0

start = time.time()

done = False
quit_game = 0

pygame.key.set_repeat(20,0)

num_agents = env.num_agents # 20

while not done:
    action_list = np.array([1 for _ in range(num_agents)])
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
                action_list[i] = 0
            if event.key == pygame.K_w:
                action_list[i] = 2

    if quit_game:
        break
    # actions should be a dict of numpy arrays
    action_dict = dict(zip(env.agent_ids, action_list)) 

    observations, reward_dict, done_dict, info = env.step(action_dict)
    env.render()
    totalReward += sum(reward_dict.values())
    done = any(done_dict.values())

print("Total final reward is ", totalReward)
# Uncomment next line to print FPS at which the game runs
# print("fps = ", env.clock.get_fps())
env.close()
