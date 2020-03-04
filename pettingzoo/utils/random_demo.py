import numpy as np
import time

def random_demo(env, render=True):
    '''
    Runs an env object with random actions.
    '''

    # env = _env(n_pursuers=n_pursuers)
    env.reset()
    
    done = False
    total_reward = 0
    observations = {}
    initial_iteration = {agent: True for agent in env.agents}
    
    # start = time.time()
    while not done:
        # game should run at 15 FPS when rendering
        if render:
            env.render()
            time.sleep(env.display_wait)
    
        for _ in env.agents:
            agent = env.agent_selection
            action = env.action_spaces[agent].sample()
            env.step(action, observe=False)
            if not initial_iteration[agent]:
                total_reward += env.rewards[agent]
                print("step reward for agent {} is {}".format(agent, env.rewards[agent]))
            initial_iteration[agent] = False
        done = all(env.dones.values())
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
