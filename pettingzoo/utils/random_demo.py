import numpy as np
import time

def random_demo(env, render=True):
    '''
    Runs an env object with random actions.
    '''

    # env = _env(n_pursuers=n_pursuers)
    env.reset()
    
    total_reward = 0
    observations = {}
    initial_iteration = {agent: True for agent in env.agents}
    dones = {agent: False for agent in env.agents}
    done = all(dones.values())
    
    # start = time.time()
    while not done:
        # game should run at 15 FPS when rendering
        if render:
            env.render()
            time.sleep(env.display_wait)
    
        for _ in env.agents:
            agent = env.agent_selection

            if not initial_iteration[agent]:
                reward, dones[agent], _ = env.last_cycle()
                total_reward += reward
                print("step reward for agent {} is {}".format(agent, reward))
            initial_iteration[agent] = False
            action = env.action_spaces[agent].sample()
            env.step(action, observe=False)
        print(" d", dones)
        done = all(dones.values())
        if done:
            print("Total reward", total_reward, "done", done)
        # # collect observations
        # for agent in env.agents:
        #     observations[agent] = env.observe(agent)
    
    # end = time.time()
    # print("FPS = ", 100/(end-start))
    if render:
        env.render()
        time.sleep(2)
    env.close()
