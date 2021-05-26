from pettingzoo.classic import rps_v1
import random
import numpy as np
from pettingzoo.test.api_test import play_test

env = rps_v1.env(max_cycles = 150)
done = False
env.reset()
observation_0, _, _, _ = env.last()
play_test(env, observation_0, 10)
for agent in env.agent_iter():
    env.render()
    obs, reward, done, _ = env.last()
    if done:
        action = None
    elif isinstance(obs, dict) and 'action_mask' in obs:
        action = random.choice(np.flatnonzero(obs['action_mask']))
    else:
        action = env.action_spaces[agent].sample()
    env.step(action)

env.close()