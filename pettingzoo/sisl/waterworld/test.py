import numpy as np
from .waterworld import env as _env
import time

n_pursuers = 5

env = _env(n_pursuers=n_pursuers)
env.reset()

done = False
total_reward = 0

# start = time.time()
while not done:
    # game should run at 15 FPS when rendering
    env.render()
    time.sleep(0.03)

    action_list = np.array([env.action_spaces[i].sample() for i in range(env.num_agents)])
    
    for a in action_list:
        reward, d, inf = env.last_cycle()
        obs =  env.step(a)
        if d:
            done = True
        total_reward += reward
    print("step reward ", total_reward)
    if done:
        print("Total reward ", total_reward)
    

# end = time.time()
# print("FPS = ", 100/(end-start))
env.render()
time.sleep(2)
env.close()

#  # for random trials
#  num_trials = 1000
#  total_reward = [0.0]*num_trials
#  for i in range(num_trials):
#      env.reset()
#      done = False
#      while not done:
#          action_list = np.array([env.action_spaces[i].sample() for i in range(env.num_agents)])
#          action_dict = dict(zip(env.agents, action_list))
#
#          observation, rewards, done_dict, info = env.step(action_dict)
#          done = any(list(done_dict.values()))
#          total_reward[i] += sum(rewards.values())
#          # print("step reward = ", sum(rewards.values()))
#          if done:
#              print("Total reward of iter ", i, total_reward[i], done)
#
#  print("Average over all trials = ", sum(total_reward)/num_trials)
#  env.close()
