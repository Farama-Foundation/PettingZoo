from pettingzoo.classic import dou_dizhu_v3
import random
import numpy as np


env = dou_dizhu_v3.env(opponents_hand_visible=False)
# print('no error')
env.reset()

# print('no error')
for agent in env.agent_iter():
    print(agent)
    # env.render()
    obs, reward, done, _ = env.last()
    # print(done)
    print(obs['observation'].shape)
    if done:
        action = None
    elif isinstance(obs, dict) and 'action_mask' in obs:
        action = random.choice(np.flatnonzero(obs['action_mask']))
    else:
        action = env.action_spaces[agent].sample()
    # print('action: ', action)
    env.step(action)
    print(env.observation_spaces)
