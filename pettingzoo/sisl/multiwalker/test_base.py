import numpy as np
from .multiwalker_base import MultiWalkerEnv

env = MultiWalkerEnv()
env.reset()
done = False

while not done:
    env.render()
    a = np.array([env.agents[0].action_space.sample() for _ in range(env.n_walkers)])
    o, r, dones, _ = env.step(a)
    done = any(dones)
    if done:
        print("done is ", done)
        break
