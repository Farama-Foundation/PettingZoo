"""Uses Stable-Baselines3 to view trained agents playing Pistonball.

Adapted from https://towardsdatascience.com/multi-agent-deep-reinforcement-learning-in-15-lines-of-code-using-pettingzoo-e0b963c0820b

Author: Elliot (https://github.com/elliottower)
"""
import glob
import os

import supersuit as ss
from stable_baselines3 import PPO

from pettingzoo.butterfly import pistonball_v6

if __name__ == "__main__":
    # Watch a game between two trained agents
    env = pistonball_v6.env(render_mode="human")

    env = ss.color_reduction_v0(env, mode="B")
    env = ss.resize_v1(env, x_size=84, y_size=84)
    env = ss.frame_stack_v1(env, 3)

    try:
        latest_policy = max(
            glob.glob(f"{env.metadata['name']}*.zip"), key=os.path.getctime
        )
    except ValueError:
        print("Policy not found.")
        exit(0)

    model = PPO.load(latest_policy)

    env.reset()
    for agent in env.agent_iter():
        obs, reward, termination, truncation, info = env.last()
        act = (
            model.predict(obs, deterministic=True)[0]
            if not termination or truncation
            else None
        )
        env.step(act)
