import os
import random
import subprocess
import sys
from test.all_modules import all_environments

import numpy as np
from PIL import Image


def generate_data(nameline, module):
    dir = f"frames/{nameline}/"
    os.mkdir(dir)
    env = module.env(render_mode="rgb_array")
    # env = gin_rummy_v0.env()
    env.reset()
    for step in range(100):
        for agent in env.agent_iter(
            env.num_agents
        ):  # step through every agent once with observe=True
            obs, rew, termination, truncation, info = env.last()
            if termination or truncation:
                action = None
            elif isinstance(obs, dict) and "action_mask" in obs:
                action = random.choice(np.flatnonzero(obs["action_mask"]))
            else:
                action = env.action_spaces[agent].sample()
            env.step(action)

        if env.terminations[agent] or env.truncations[agent]:
            env.reset()

        ndarray = env.render()
        # tot_size = max(ndarray.shape)
        # target_size = 500
        # ratio = target_size / tot_size
        # new_shape = (int(ndarray.shape[1] * ratio), int(ndarray.shape[0] * ratio))
        im = Image.fromarray(ndarray)
        # im  = im.resize(new_shape, Image.ANTIALIAS)
        im.save(f"{dir}{str(step).zfill(3)}.png")
        # print(text)
    env.close()
    render_gif_image(nameline)
    # num_games = 0
    # while num_games < 10000:
    #     for i in range(2):
    #         text = text_to_display[i]
    #         # surf = font.render(text,False,(255,255,255),(0,0,0))
    #         # screen.blit(surf, (0,0))


def render_gif_image(name):
    ffmpeg_command = ["convert", f"frames/{name}/*.png", f"gifs/{name}.gif"]
    print(" ".join(ffmpeg_command))
    subprocess.run(ffmpeg_command)


def render_all():
    for name, module in all_environments.items():
        if "classic" not in name:
            nameline = name.replace("/", "_")
            generate_data(nameline, module)
            # render_gif_image(nameline)


if __name__ == "__main__":
    name = sys.argv[1]
    if name == "all":
        render_all()
    else:
        module = all_environments[name]
        nameline = name.replace("/", "_")

        generate_data(nameline, module)
