from pettingzoo.magent import adversarial_pursuit_v2
import random
import numpy as np

env = adversarial_pursuit_v2.env(minimap_mode=True, extra_features=True)
env.reset()
for agent in env.agent_iter():
        # env.render()
    obs, reward, done, _ = env.last()
    # print(agent)
    # print(obs.shape)
    if done:
        action = None
    elif isinstance(obs, dict) and 'action_mask' in obs:
        action = random.choice(np.flatnonzero(obs['action_mask']))
    else:
        action = env.action_spaces[agent].sample()
    env.step(action)
