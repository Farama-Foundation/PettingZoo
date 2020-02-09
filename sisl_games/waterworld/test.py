import numpy as np
from .waterworld import env as _env
import time

n_pursuers = 5

env = _env(n_pursuers = n_pursuers)
env.reset()

done = False
total_reward = 0

# start = time.time()
# for _ in range(100):
while not done:
    # game should run at 15 FPS when rendering
    env.render()
    time.sleep(0.03)
    
    action_list = np.array([env.action_space_dict[i].sample() for i in range(env.num_agents)])
    action_dict = dict(zip(env.agent_ids, action_list))
    
    observation, rewards, done_dict, info = env.step(action_dict)
    done = any(list(done_dict.values()))
    total_reward += sum(rewards.values())
    print("step reward", sum(rewards.values()))
    if done:
        print("Total reward", total_reward, "done", done)

# end = time.time()
# print("FPS = ", 100/(end-start))
env.render()
time.sleep(2)
env.close()
