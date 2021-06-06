from math import e
from pettingzoo.magent import combined_arms_v4
import random
import numpy as np

env = combined_arms_v4.env(map_size=16)
env.reset()

for agent in env.agent_iter():
#    env.render()

    obs, reward, done, _ = env.last()
    # print("new agent")
    # print(obs.shape)
    if done:
        action = None
    elif isinstance(obs, dict) and 'action_mask' in obs:
        action = random.choice(np.flatnonzero(obs['action_mask']))
    else:
        action = env.action_spaces[agent].sample()
    env.state()
    env.step(action)