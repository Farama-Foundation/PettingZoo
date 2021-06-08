from pettingzoo.magent import gather_v3
import random
import numpy as np

env = gather_v3.env(minimap_mode=False, extra_features=True)

env.reset()
env.state()
# for agent in env.agent_iter():
#     obs, reward, done, _ = env.last()
#     if done:
#         action = None
#     elif isinstance(obs, dict) and 'action_mask' in obs:
#         action = random.choice(np.flatnonzero(obs['action_mask']))
#     else:
#         action = env.action_spaces[agent].sample()
#     env.step(action)