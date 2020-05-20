import random
import time
import numpy as np
import json

from pettingzoo.tests.all_modules import all_environments
from pettingzoo.classic import gin_rummy_v0
from PIL import Image
import os
import scipy.misc
import sys

name = sys.argv[1]
module = all_environments[name]

nameline = name[name.index("/")+1:]
dir = f"frames/{nameline}/"
os.mkdir(dir)
env = module.env()
#env = gin_rummy_v0.env()
env.reset()
for step in range(100):
    for agent in env.agent_order:  # step through every agent once with observe=True
        if env.dones[agent]:
            env.reset()
            break
        if 'legal_moves' in env.infos[agent]:
            action = random.choice(env.infos[agent]['legal_moves'])
        else:
            action = env.action_spaces[agent].sample()
        env.step(action)

    ndarray = env.render()
    tot_size = max(ndarray.shape)
    target_size = 500
    ratio = target_size/tot_size
    new_shape = (int(ndarray.shape[1]*ratio),int(ndarray.shape[0]*ratio))
    im = Image.fromarray(ndarray)
    #im  = im.resize(new_shape, Image.ANTIALIAS)
    im.save(f"{dir}{str(step).zfill(3)}.png")
    #print(text)


# num_games = 0
# while num_games < 10000:
#     for i in range(2):
#         text = text_to_display[i]
#         # surf = font.render(text,False,(255,255,255),(0,0,0))
#         # screen.blit(surf, (0,0))
