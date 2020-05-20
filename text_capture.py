import random
import time
import numpy as np
import json

from pettingzoo.tests.all_modules import all_environments
from pettingzoo.classic import gin_rummy_v0

def shrink_lines(data,max_height,max_width):
    lines = data.split("\r\n")[:max_height]
    for i in range(len(lines)):
        lines[i] = lines[i][:max_width]
    return "\r\n".join(lines)

for name,module in all_environments.items():
    if "classic" not in name:
        continue
    env = module.env()
    #env = gin_rummy_v0.env()
    env.reset()
    first_val = env.render()
    max_line_len = max(len(l) for l in first_val.split("\n"))
    line_height = len(first_val.split("\n"))
    line_len = max(50,min(max_line_len,80))
    line_height = max(25,min(line_height+10,35))
    print(max_line_len)
    first_line = '{"version": 2, "width": %d, "height": %d, "timestamp": 1590001545, "env": {"SHELL": "/bin/bash", "TERM": "xterm-256color"}}'%(line_len,line_height)
    lines = [first_line]

    for step in range(25):
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
        out_line = [step*0.2,'o',shrink_lines(endline_correct,line_height,line_len)]
        lines.append(json.dumps(out_line))
    nameline = name.replace("/","_")
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
