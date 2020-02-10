import numpy as np
from .pursuit import env as _env
import time

# from .utils import two_d_maps

xs = 5
ys = 5
obs_range = 3
n_evaders = 1
n_pursuers = 2

# obs_range should be odd 3, 5, 7, etc
# env = _env(n_pursuers = n_pursuers, n_evaders = n_evaders, xs = xs, ys = ys, obs_range = obs_range)
env = _env()

done = False

global _quit_loop, _actions, _agent_id
_quit_loop = np.array([0])
_actions = np.array([4]*env.num_agents)
_agent_id = np.array([0])
env.reset()
# controlling only the pursuers
import matplotlib.pyplot as plt
fig, ax = plt.subplots()

def on_key(event):
    # print('you pressed', event.key)
    if event.key == "escape":
        print("escape")
        _quit_loop[0] = 1
        # break
    if event.key == "backspace":
        env.reset()
    if event.key == "j":
        # pressing 'j' moves the focus of control to the next agent
        # control rolls over to the first agent
        _agent_id[0] = (_agent_id[0] + 1) % env.num_agents
    if event.key == "left":
        # p1: left
        _actions[_agent_id[0]] = 0
    if event.key == "right":
        # p1: right
        _actions[_agent_id[0]] = 1
    if event.key == "up":
        # p1: up
        _actions[_agent_id[0]] = 3
    if event.key == "down":
        # p1: down
        _actions[_agent_id[0]] = 2

cid = fig.canvas.mpl_connect('key_press_event', on_key)

done = False
num_frames = 0
total_reward = 0
# start = time.time()
# for _ in range(100):
while not done:
    env.render()
    if _quit_loop[0]:
        break
    # actions should be a dict of numpy arrays
    action_dict = dict(zip(env.agent_ids, _actions))
    
    observation, rewards, done_dict, info = env.step(action_dict)
    done = any(list(done_dict.values()))
    total_reward += sum(rewards.values())
    print("step reward = ", sum(rewards.values()))
    if done:
        print("Total reward", total_reward, done)
    
    _actions = np.array([4]*env.num_agents)

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
#          if _quit_loop[0]:
#              break
#          # actions should be a dict of numpy arrays
#          action_dict = dict(zip(env.agent_ids, _actions))
#          
#          observation, rewards, done_dict, info = env.step(action_dict)
#          done = any(list(done_dict.values()))
#          total_reward[i] += sum(rewards.values())
#          # print("step reward = ", sum(rewards.values()))
#          if done:
#              print("Total reward of iter ", i, total_reward[i], done)
#          
#          _actions = np.array([4]*env.num_agents)
#  
#  print("Average over all trials = ", sum(total_reward)/num_trials)
#  env.close()
