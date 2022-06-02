import subprocess

from pettingzoo.test.all_modules import all_environments

# procs = []
for name, module in all_environments.items():
    if "classic" not in name:
        continue

    nameline = name.replace("/", "_")
    proc = subprocess.run(
        ["asciicast2gif", f"gif_data/{nameline}.json", f"gifs/{nameline}.gif"]
    )
    # procs.append(proc)
    # if len(procs) >= 3:
    #     for p in procs:
    #         p.wait()
    #     procs = []

#
#
# num_games = 0
# while num_games < 10000:
#     for i in range(2):
#         text = text_to_display[i]
#         # surf = font.render(text,False,(255,255,255),(0,0,0))
#         # screen.blit(surf, (0,0))
