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
    initial_iteration = {agent: True for agent in env.agents}
    dones = {agent: False for agent in env.agents}
    done = all(dones.values())

    # start = time.time()
    while not done:
        # game should run at 15 FPS when rendering
        if render:
            env.render()
            time.sleep(display_wait)

        # for _ in env.agents:
        agent = env.agent_selection
        if not dones[agent]:
            if not initial_iteration[agent]:
                reward, dones[agent], _ = env.last()
                total_reward += reward
                print("step reward for agent {} is {} done: {}".format(
                    agent, reward, dones[agent]))
            initial_iteration[agent] = False

            if 'legal_moves' in env.infos[agent]:
                action = random.choice(env.infos[agent]['legal_moves'])
            else:
                action = env.action_spaces[agent].sample()
            env.step(action, observe=False)
        done = all(dones.values())
        if done:
            print("Total reward", total_reward, "done", done)

    # end = time.time()
    # print("FPS = ", 100/(end-start))
    if render:
        env.render()
        time.sleep(2)
    env.close()
