import time
import random


def random_demo(env, render=True, cycles=100000000):
    '''
    Runs an env object with random actions.
    '''

    env.reset()

    if hasattr(env, 'display_wait'):
        display_wait = env.display_wait
    else:
        display_wait = 0.0

    total_reward = 0
    done = False

    for cycle in range(cycles):
        for agent in env.agent_iter(len(env.agents)):
            if render:
                env.render()
                time.sleep(display_wait)

            obs, reward, done, _ = env.last()
            total_reward += reward
            if done:
                action = None
            elif 'legal_moves' in env.infos[agent]:
                action = random.choice(env.infos[agent]['legal_moves'])
            else:
                action = env.action_spaces[agent].sample()
            env.step(action)

    print("Total reward", total_reward, "done", done)

    if render:
        env.render()
        time.sleep(2)

    env.close()

    return total_reward
