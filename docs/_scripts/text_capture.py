import json
import random

import numpy as np

from pettingzoo.test.all_modules import all_environments


def shrink_lines(data, max_height, max_width):
    lines = data.split("\r\n")[:max_height]
    for i in range(len(lines)):
        lines[i] = lines[i][:max_width]
    return "\r\n".join(lines)


for name, module in all_environments.items():
    if "classic/" not in name:
        continue
    env = module.env()
    # env = gin_rummy_v0.env()
    env.reset()

    all_text = [env.render()]
    for step in range(25):
        # for agent in env.agent_iter:  # step through every agent once with observe=True
        agent = env.agent_selection
        if env.terminations[agent] or env.truncations[agent]:
            env.reset()
        agent = env.agent_selection

        obs, rew, termination, truncation, info = env.last()
        if termination or truncation:
            action = None
        elif isinstance(obs, dict) and "action_mask" in obs:
            action = random.choice(np.flatnonzero(obs["action_mask"]))
        else:
            action = env.action_spaces[agent].sample()
        env.step(action)

        text = env.render()
        all_text.append(text)

    max_line_len = max(max(len(ln) for ln in val.split("\n")) for val in all_text)
    line_height = max(len(val.split("\n")) for val in all_text)
    line_len = min(max_line_len + 1, 80)
    line_height = min(line_height + 1, 50)
    print(max_line_len)
    first_line = (
        '{"version": 2, "width": %d, "height": %d, "timestamp": 1590001545, "env": {"SHELL": "/bin/bash", "TERM": "xterm-256color"}}'
        % (line_len, line_height)
    )
    lines = [first_line]

    for step, text in enumerate(all_text):
        endline_correct = text.replace("\n", "\r\n") + "\r\n\r\n"
        begl = "\u001b[H\u001b[2J"  # \u001b[00m$ "
        if name != "classic/go":
            out_line = [
                step * 0.3,
                "o",
                begl + shrink_lines(endline_correct, line_height, line_len),
            ]
        else:
            out_line = [step * 0.3, "o", begl + endline_correct]
        lines.append(json.dumps(out_line))
    nameline = name.replace("/", "_")
    with open(f"gif_data/{nameline}.json", "w") as fh:
        fh.write("\n".join(lines))

#
#
# num_games = 0
# while num_games < 10000:
#     for i in range(2):
#         text = text_to_display[i]
#         # surf = font.render(text,False,(255,255,255),(0,0,0))
#         # screen.blit(surf, (0,0))
