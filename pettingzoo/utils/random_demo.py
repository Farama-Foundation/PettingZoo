import time
import random


def random_demo(env, render=True):
    '''
    Runs an env object with random actions.
    '''

    # env = _env(n_pursuers=n_pursuers)
    env.reset()

    if hasattr(env, 'display_wait'):
        display_wait = env.display_wait
    else:
        display_wait = 0.0

    total_reward = 0
    done = False

    # start = time.time()
    while not done:
        # game should run at 15 FPS when rendering
        if render:
            env.render()
            time.sleep(display_wait)

        # for _ in env.agents:
        agent = env.agent_selection
        reward, done, _ = env.last()
        if not done:
            if 'legal_moves' in env.infos[agent]:
                action = random.choice(env.infos[agent]['legal_moves'])
            else:
                action = env.action_spaces[agent].sample()
            env.step(action, observe=False)
        else:
            print("Total reward", total_reward, "done", done)

    # end = time.time()
    # print("FPS = ", 100/(end-start))
    if render:
        env.render()
        time.sleep(2)

    env.close()

    return total_reward
