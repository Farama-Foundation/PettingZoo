#!/usr/bin/env python3

import numpy as np
from .multi_walker import MultiWalkerEnv

n_walkers = 3
reward_mech = 'local'
env = MultiWalkerEnv(n_walkers=n_walkers, reward_mech=reward_mech)
env.reset()
done = False

while not done:
    env.render()
    a = np.array([env.agents[0].action_space.sample() for _ in range(n_walkers)])
    o, r, done, _ = env.step(a)
    print("Rewards:", r)
    if done:
        print("done is ", done)
        break
