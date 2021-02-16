import time
import random
import numpy as np


def random_demo(env, render=True, episodes=1):
    '''
    Runs an env object with random actions.
    '''

    total_reward = 0
    done = False
    run_episodes = 0

    while True:
        env.reset()
        for agent in env.agent_iter(len(env.agents)):
            if render:
                env.render()

            obs, reward, done, _ = env.last()
            total_reward += reward
            if done:
                action = None
            elif isinstance(obs, dict) and 'action_mask' in obs:
                action = random.choice(np.flatnonzero(obs['action_mask']))
            else:
                action = env.action_spaces[agent].sample()
            env.step(action)

            run_episodes += 1

        if run_episodes == episodes:
            if render:
                env.close()
            break

    print("Average total reward", total_reward / episodes)

    return total_reward
