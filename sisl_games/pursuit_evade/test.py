#!/usr/bin/env python3

import numpy as np
from .pursuit_evade import env as _env
import time

# from .utils import two_d_maps

xs = 5
ys = 5
n_evaders = 1
n_pursuers = 2

# map_mat = two_d_maps.rectangle_map(xs, ys) 

# obs_range should be odd 3, 5, 7, etc
env = _env() #n_evaders=n_evaders, n_pursuers=n_pursuers)

done = False

global _quit_loop, _totalReward, _actions
_quit_loop = 0
_totalReward = 0
_actions = np.array([4]*env.num_agents)
env.reset()
# controlling only the pursuers
import matplotlib.pyplot as plt
fig, ax = plt.subplots()

def on_key(event):
    # print('you pressed', event.key)
    if event.key == "escape":
        print("escape")
        _quit_loop = 1
        # break
    if event.key == "backspace":
        env.reset()
        _totalReward = 0
    if event.key == "left":
        # p1: left
        _actions[0] = 0
    if event.key == "right":
        # p1: right
        _actions[0] = 1
    if event.key == "up":
        # p1: up
        _actions[0] = 3
    if event.key == "down":
        # p1: down
        _actions[0] = 2
    if event.key == "4":
        # p2: left
        _actions[1] = 0
    if event.key == "6":
        # p2: right
        _actions[1] = 1
    if event.key == "8":
        # p2: up
        _actions[1] = 3
    if event.key == "5":
        # p2: down
        _actions[1] = 2

cid = fig.canvas.mpl_connect('key_press_event', on_key)

done = False
num_frames = 0
# start = time.time()
# for _ in range(100):
while not done:
    env.render()
    # print("_quit_loop", _quit_loop)
    if _quit_loop:
        break
    # actions should be a dict of numpy arrays: {0: array([0,1,0])}
    action_dict = dict(zip(env.agent_ids, [np.array([0]*env.n_act_agents) for _ in range(env.num_agents)])) # no action = [0,1,0]
    for idx, val in enumerate(_actions):
        action_dict[idx][val] = 1
    observation, rewards, done_dict, info = env.step(action_dict)
    done = any(list(done_dict.values()))
    if done:
        print("rewards", rewards, done)
    
    _actions = np.array([4]*env.num_agents)

# end = time.time()
# print("FPS = ", 100/(end-start))
env.render()
time.sleep(3)
env.close()
