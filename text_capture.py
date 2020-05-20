import random
import time
import numpy as np
import json

from pettingzoo.tests.all_modules import all_environments
from pettingzoo.classic import gin_rummy_v0


for name,module in all_environments.items():
    if "classic" not in name:
        continue
    first_line = '{"version": 2, "width": 82, "height": 24, "timestamp": 1590001545, "env": {"SHELL": "/bin/bash", "TERM": "xterm-256color"}}'
    lines = [first_line]
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

        text = env.render()
        #print(text)
        endline_correct = text.replace("\n","\r\n")+"\r\n\r\n"
        out_line = [step*0.2,'o',endline_correct]
        lines.append(json.dumps(out_line))
    nameline = name[name.index("/")+1:]
    with open(f"gif_data/{nameline}.json",'w') as fh:
        fh.write("\n".join(lines))

#
#
# num_games = 0
# while num_games < 10000:
#     for i in range(2):
#         text = text_to_display[i]
#         # surf = font.render(text,False,(255,255,255),(0,0,0))
#         # screen.blit(surf, (0,0))
