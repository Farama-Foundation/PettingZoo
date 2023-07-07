"""Uses Stable-Baselines3 to view trained agents playing Rock-Paper-Scissors.

Adapted from https://towardsdatascience.com/multi-agent-deep-reinforcement-learning-in-15-lines-of-code-using-pettingzoo-e0b963c0820b

Authors: Jordan (https://github.com/jkterry1), Elliot (https://github.com/elliottower)
"""

import glob
import os

from stable_baselines3 import PPO

from pettingzoo.classic import rps_v2

env = rps_v2.env(render_mode="human")

latest_policy = max(glob.glob("rps_*.zip"), key=os.path.getctime)
model = PPO.load(latest_policy)

env.reset()
for agent in env.agent_iter():
    obs, reward, termination, truncation, info = env.last()
    if termination or truncation:
        act = None
    else:
        act = model.predict(obs, deterministic=True)[0]
    env.step(act)
