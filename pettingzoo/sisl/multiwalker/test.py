import numpy as np
from .multiwalker import env as _env
from pettingzoo.utils import random_demo
import time

n_walkers = 3

env = _env(n_walkers=n_walkers)
env.reset()

done = False
total_reward = 0

# start = time.time()
random_demo(env, render=True)

# end = time.time()
# print("FPS = ", 100/(end-start))

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
