import numpy as np
import time

def random_demo(env):
    '''
    Runs an env object with random actions.
    '''

    # env = _env(n_pursuers=n_pursuers)
    env.reset()
    
    done = False
    total_reward = 0
    observations = {}
    
    # start = time.time()
    while not done:
        # game should run at 15 FPS when rendering
        env.render()
        time.sleep(env.display_wait)
    
        for _ in env.agents:
            agent = env.agent_selection
            action = env.action_spaces[agent].sample()
            env.step(action, observe=False)

        # # collect observations
        # for agent in env.agents:
        #     observations[agent] = env.observe(agent)
        rewards = env.env.rewards
        dones = env.env.dones

        done = all(dones.values())
        total_reward += sum(rewards.values())
        print("step reward", sum(rewards.values()))
        if done:
            print("Total reward", total_reward, "done", done)
    
    # end = time.time()
    # print("FPS = ", 100/(end-start))
    env.render()
    time.sleep(2)
    env.close()
