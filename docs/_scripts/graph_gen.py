import math
import os
import subprocess
from collections import defaultdict

from pettingzoo.test.all_modules import all_environments


def generate_cycle_words(agents, is_classic):
    if is_classic:
        words = []
        for agent in agents:
            words.append("env")
            words.append(agent)
    else:
        if len(agents) >= 10:
            types = []
            type_nums = defaultdict(list)
            for name in agents:
                splitname = name.split("_")
                type = splitname[0]
                type_nums[type].append(int(splitname[1]))
                if type not in types:
                    types.append(type)
            if len(types) == 1:
                words = ["env"]
                words.append(agents[0])
                nums = type_nums[types[0]]
                type_range = f"{type}_[{nums[1]}...{nums[-1]}]"
                words.append(type_range)
            else:
                words = ["env"]
                for type in types:
                    tyrange = list(range(type_nums[type][0], type_nums[type][-1] + 1))
                    assert tyrange == type_nums[type]
                    type_range = f"{type}_[{tyrange[0]}...{tyrange[-1]}]"
                    words.append(type_range)
        else:
            words = ["env"] + agents
    return words


def generate_graphviz(words):
    max_chars = max(len(w) for w in words)
    node_width = max_chars * 0.1 + 0.2
    innards = ""  # "overlap = false;\n"
    innards += f'node [shape = circle,fixedsize=true,width={node_width},fontname="Segoe UI"];\n'
    for i, word in enumerate(words):
        theta = 2 * math.pi * i / len(words)
        rad_const = 1.0 if len(words) <= 3 else 0.8
        rad = (len(words)) * rad_const * node_width / math.pi
        xpos = rad * math.sin(theta)
        ypos = rad * math.cos(theta)
        innards += f'a{i} [label="{word}",pos="{xpos},{ypos}!"];\n'
    for i in range(len(words) - 1):
        innards += f"a{i} -> a{i+1};\n"
    innards += f"a{len(words)-1} -> a{0};\n"
    return "digraph G {\n%s\n}" % innards


for name, module in list(all_environments.items()):
    env = module.env()
    agents = env.possible_agents
    words = generate_cycle_words(env.possible_agents, "classic/" in name)
    vis_code = generate_graphviz(words)
    code_path = "graphviz/" + name + ".vis"
    os.makedirs(os.path.dirname(code_path), exist_ok=True)
    with open(code_path, "w") as file:
        file.write(vis_code)
    out_path = f"docs/assets/img/aec/{name.replace('/','_')}_aec.svg"
    cmd = ["neato", "-Tsvg", "-o", out_path, code_path]
    print(" ".join(cmd))
    subprocess.Popen(cmd)
