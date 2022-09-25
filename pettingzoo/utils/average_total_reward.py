import random

import numpy as np


def average_total_reward(env, max_episodes=100, max_steps=10000000000):
    """Calculates the average total reward over the episodes.

    Runs an env object with random actions until either max_episodes or
    max_steps is reached.
    Reward is summed across all agents, making it unsuited for use in zero-sum
    games.
    """
    total_reward = 0
    total_steps = 0
    num_episodes = 0

    for episode in range(max_episodes):
        if total_steps >= max_steps:
            break

        env.reset()
        for agent in env.agent_iter():
            obs, reward, termination, truncation, _ = env.last(observe=False)
            total_reward += reward
            total_steps += 1
            if termination or truncation:
                action = None
            elif isinstance(obs, dict) and "action_mask" in obs:
                action = random.choice(np.flatnonzero(obs["action_mask"]))
            else:
                action = env.action_space(agent).sample()
            env.step(action)

        num_episodes = episode + 1
    print("Average total reward", total_reward / num_episodes)

    return total_reward / num_episodes
