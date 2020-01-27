#!/usr/bin/env python3

import numpy as np
from .multi_walker import env as _env
import time

n_walkers = 3

env = _env(n_walkers = n_walkers)
env.reset()

done = False
# start = time.time()
while not done:
    # game should run at 15 FPS when rendering
    env.render()
    time.sleep(0.04)
    
    action_list = np.array([env.action_space_dict[i].sample() for i in range(env.num_agents)])
    action_dict = dict(zip(env.agent_ids, action_list))
    
    observation, rewards, done_dict, info = env.step(action_dict)
    done = any(list(done_dict.values()))
    print("rewards", rewards)
    if done:
        print("rewards", rewards, "done", done)

# end = time.time()
# print("FPS = ", 100/(end-start))
env.render()
time.sleep(2)
env.close()
