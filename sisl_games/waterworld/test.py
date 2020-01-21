#!/usr/bin/env python3

from .waterworld import MAWaterWorld

env = MAWaterWorld(5, 10, obs_loc=None)
obs = env.reset()
done = False

while not done:
    obs, rew, done, _ = env.step(env.np_random.randn(10) * .5)
    if rew.sum() > 0:
        print("Reward = ", rew)
    env.render()
    
env.close()