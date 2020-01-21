#!/usr/bin/env python3

import numpy as np
from .cooperative_pong import env as _env
import pygame

# TODO: change these values for testing
BALL_SPEED, P1_SPEED, P2_SPEED, BOUNCE_RANDOMNESS = 18, 25, 25, 0
# Defaults are 18, 25, 25, 0 as used in cooperative_pong.py. There parameters need not be intialized while creating an env instance.

env = _env(BALL_SPEED, P1_SPEED, P2_SPEED)

done = False
quit_loop = 0

totalReward = 0
# Fixed: Key held down will generate multiple events
pygame.key.set_repeat(20,0)

while not done:
    
    actionList = np.array([0]*env.num_agents) # do nothing
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
                totalReward = 0
            if event.key == pygame.K_w:
                # player1.moveup()
                actionList[0] = 1
            if event.key == pygame.K_s:
                # player1.movedown()
                actionList[0] = 2
            if event.key == pygame.K_UP:
                # player2.moveup()
                actionList[1] = 1
            if event.key == pygame.K_DOWN:
                # player2.movedown()
                actionList[1] = 2
    if quit_loop:
        break
    
    # actions should be a dict of numpy arrays: {0: array([0,1,0])}
    action_dict = dict(zip(env.agent_ids, [np.array([0,0,0]) for _ in range(env.num_agents)])) # no action = [0,1,0]
    for idx, val in enumerate(actionList):
        action_dict[idx][val] = 1
    
    observation, rewards, dones, info = env.step(action_dict)
    env.render()
    totalReward += rewards[0]
    done = dones[0]
    pygame.event.pump()
    # env.plot_obs(observation, "obs")
    # break

assert (totalReward == env.env.score), "Final score = {} and reward = {} are not the same".format(env.score, totalReward)
print("Final reward is {0:.2f}".format(totalReward))
# Uncomment next line to print FPS at which the game runs
# print("fps = ", env.env.clock.get_fps())

# pygame.time.wait(3000)
env.close()
