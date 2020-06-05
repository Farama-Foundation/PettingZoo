from gym.spaces import Discrete, Box
import numpy as np
import warnings
import magent
from pettingzoo import AECEnv
import math
from pettingzoo.magent.render import Renderer
from pettingzoo.utils import agent_selector
from .magent_env import markov_env
from .markov_env_wrapper import markov_env_wrapper
import os
from magent.utility import FontProvider
from gym.utils import seeding


def env(map_size=200, seed=None):
    return markov_env_wrapper(arrange_markov_env(map_size, seed=seed))


def load_config(map_size):
    gw = magent.gridworld
    cfg = gw.Config()

    cfg.set({"map_width": map_size, "map_height": map_size})
    cfg.set({"minimap_mode": True})
    cfg.set({"embedding_size": 12})

    goal = cfg.register_agent_type(
        "goal",
        {'width': 1, 'length': 1,

         'can_absorb': True
         }
    )

    agent = cfg.register_agent_type(
        "agent",
        {'width': 1, 'length': 1, 'hp': 10, 'speed': 2,
         'view_range': gw.CircleRange(6),
         'step_recover': -10.0/400,

         'step_reward': 0,
         })

    g_goal = cfg.add_group(goal)
    g_agent = cfg.add_group(agent)

    g = gw.AgentSymbol(g_goal, 'any')
    a = gw.AgentSymbol(g_agent, 'any')

    cfg.add_reward_rule(gw.Event(a, 'collide', g), receiver=a, value=10)

    return cfg


def remove_wall(d, cur_pos, wall_set, unit):
    if d == 0:
        for i in range(0, unit):
            for j in range(0, unit):
                temp = (cur_pos[0] + i, cur_pos[1] + unit + j)
                if temp in wall_set:
                    wall_set.remove(temp)
    elif d == 1:
        for i in range(0, unit):
            for j in range(0, unit):
                temp = (cur_pos[0] - unit + i, cur_pos[1] + j)
                if temp in wall_set:
                    wall_set.remove(temp)
    elif d == 2:
        for i in range(0, unit):
            for j in range(0, unit):
                temp = (cur_pos[0] + i, cur_pos[1] - unit + j)
                if temp in wall_set:
                    wall_set.remove(temp)
    elif d == 3:
        for i in range(0, unit):
            for j in range(0, unit):
                temp = (cur_pos[0] + unit + i, cur_pos[1] + j)
                if temp in wall_set:
                    wall_set.remove(temp)


def dfs(x, y, width, height, unit, wall_set, np_random):
    pos = set()
    trace = list()
    pos.add((x, y))
    trace.append((x, y))

    max_x = x + width
    max_y = y + height

    d = np_random.randint(0,4)
    pos_list = []
    flag = 0
    while len(trace) > 0:
        if flag == 4:
            cur_pos = trace[-1]
            trace.pop()
            if np_random.randint(0,2) == 0:
                remove_wall(d, cur_pos, wall_set, unit)
            flag = 0
        if len(trace) == 0:
            break
        cur_pos = list(trace[-1])
        if d == 0:
            cur_pos[1] = max(y, cur_pos[1] - 2 * unit)
        elif d == 1:
            cur_pos[0] = min(max_x, cur_pos[0] + 2 * unit)
        elif d == 2:
            cur_pos[1] = min(max_y, cur_pos[1] + 2 * unit)
        elif d == 3:
            cur_pos[0] = max(x, cur_pos[0] - 2 * unit)
        if tuple(cur_pos) in pos:
            d = (d + 1) % 4
            flag += 1
        else:
            remove_wall(d, cur_pos, wall_set, unit)
            trace.append(tuple(cur_pos))
            pos.add(tuple(cur_pos))
            d = np_random.randint(0,4)


def clean_pos_set_convert_to_list(pos_set, pos_list):
    for v in pos_list:
        if v in pos_set:
            pos_set.remove(v)
    return list(pos_set)


def draw_line(x, y, width, height):
    pos_set = []
    for r in range(height):
        for c in range(width):
            pos_set.append((x + c, y + r))
    return pos_set


def open_the_door(x_s, y_s, w, h, unit):
    pos_list = []
    n_door = 15
    random_horizon_list_x = [x_s + (2 * np.random.choice(w // 2 // unit, n_door) + 1) * unit, x_s + (2 * np.random.choice(w // 2 // unit, n_door) - 1) * unit]
    random_vertical_list_y = [y_s + (2 * np.random.choice(h // 2 // unit, n_door) + 1) * unit, y_s + (2 * np.random.choice(h // 2 // unit, n_door) + 1) * unit]

    y_e = y_s + h - unit
    for v in random_horizon_list_x[0]:
        pos_list.extend([(v, y_s), (v + 1, y_s), (v, y_s + 1), (v + 1, y_s + 1)])
    for v in random_horizon_list_x[1]:
        pos_list.extend([(v, y_e), (v + 1, y_e), (v, y_e + 1), (v + 1, y_e + 1)])

    x_e = x_s + w - unit
    for v in random_vertical_list_y[0]:
        pos_list.extend([(x_s, v), (x_s, v + 1), (x_s + 1, v), (x_s + 1, v + 1)])
    for v in random_vertical_list_y[1]:
        pos_list.extend([(x_e, v), (x_e, v + 1), (x_e + 1, v), (x_e + 1, v + 1)])

    return pos_list


def create_maze(pos, width, height, unit, font_area, np_random):
    # draw block: with rect: left(x), top(y), width, height
    pos_set = []
    for i in range(height):
        if i % 2 == 0:
            pos_set.extend(draw_line(pos[0], pos[1] + i * unit, width * unit, unit))
            pos_set.extend(draw_line(pos[0], pos[1] + font_area[1] + i * unit, width * unit, unit))
            pos_set.extend(draw_line(pos[0] + i * unit, pos[1] + height * unit, unit, font_area[1]))
            pos_set.extend(draw_line(pos[0] + font_area[0] + i * unit, pos[1] + height * unit, unit, font_area[1]))

    for i in range(width):
        if i % 2 == 0:
            pos_set.extend(draw_line(pos[0] + i * unit, pos[1], unit, height * unit))
            pos_set.extend(draw_line(pos[0] + i * unit, pos[1] + font_area[1], unit, height * unit))
            pos_set.extend(draw_line(pos[0], pos[1] + i * unit, height * unit, unit))
            pos_set.extend(draw_line(pos[0] + font_area[0], pos[1] + i * unit, height * unit, unit))

    pos_set = set(pos_set)

    dfs(pos[0] + 2, pos[1] + 2, (width - 1) * unit, (height - 1) * unit, unit, pos_set, np_random)  # north
    dfs(pos[0] + 2, pos[1] + (height - 2) * unit, (height - 1) * unit, (width + 3) * unit, unit, pos_set, np_random)  # west
    dfs(pos[0] + height * unit, pos[1] + font_area[1] - unit, (width - height) * unit, (height - 1) * unit, unit, pos_set, np_random)  # south
    dfs(pos[0] + font_area[0] - unit, pos[1] + (height - 2) * unit, (height - 1) * unit, font_area[1] - (height + 1) * unit, unit, pos_set, np_random)  # east

    temp = []
    temp.extend(open_the_door(pos[0], pos[1], font_area[0] + height * unit, font_area[1] + height * unit, unit))
    res = clean_pos_set_convert_to_list(pos_set, temp)
    return res


def draw_split_line(x, y, width, height, split=10):
    pos_set = []
    if height > width:
        splits = set(np.random.choice(height // 2, split) * 2)
        for r in range(height):
            if r in splits or (r - 1 in splits):
                continue
            for c in range(width):
                pos_set.append((x + c, y + r))
    else:
        splits = set(np.random.choice(width // 2, split) * 2)
        for r in range(height):
            for c in range(width):
                if c in splits or (c - 1 in splits):
                    continue
                pos_set.append((x + c, y + r))

    return pos_set


def create_naive_maze(pos, width, height, unit, font_area):
    pos_set = []
    for i in range(height):
        if i % 2 == 0:
            pos_set.extend(draw_split_line(pos[0], pos[1] + i * unit, width * unit, unit))
            pos_set.extend(draw_split_line(pos[0], pos[1] + font_area[1] + i * unit, width * unit, unit))
            pos_set.extend(draw_split_line(pos[0] + i * unit, pos[1] + height * unit, unit, font_area[1] - height * unit))
            pos_set.extend(draw_split_line(pos[0] + font_area[0] + i * unit, pos[1] + height * unit, unit, font_area[1] - height * unit))

    return pos_set


def load_config(map_size):
    gw = magent.gridworld
    cfg = gw.Config()

    cfg.set({"map_width": map_size, "map_height": map_size})
    cfg.set({"minimap_mode": True})
    cfg.set({"embedding_size": 12})

    goal = cfg.register_agent_type(
        "goal",
        {'width': 1, 'length': 1,

         'can_absorb': True
         }
    )

    agent = cfg.register_agent_type(
        "agent",
        {'width': 1, 'length': 1, 'hp': 10, 'speed': 2,
         'view_range': gw.CircleRange(6),
         'step_recover': -10.0/400,

         'step_reward': 0,
         })

    g_goal = cfg.add_group(goal)
    g_agent = cfg.add_group(agent)

    g = gw.AgentSymbol(g_goal, 'any')
    a = gw.AgentSymbol(g_agent, 'any')

    cfg.add_reward_rule(gw.Event(a, 'collide', g), receiver=a, value=10)

    return cfg


def generate_map(env, np_random, map_size, goal_handle, handles):
    # random message
    cwd = os.path.dirname(__file__)
    font = FontProvider(os.path.join(cwd,'data/basic.txt'))
    n_msg = int(np_random.randint(1, 4+1))
    messages = []
    for i in range(n_msg):
        length = np_random.randint(2, 9+1)
        tmp = []
        for j in range(length):
            tmp.append(np_random.randint(0x20, 0x7E+1))
        messages.append(tmp)

    center_x, center_y = map_size // 2, map_size // 2

    # create maze: left pos, width, height
    radius = 90
    pos_list = create_maze([center_x - radius, center_y - radius], radius + 1, 15, 2, font_area=[radius * 2 - 28, radius * 2 - 28], np_random=np_random)
    env.add_walls(method="custom", pos=pos_list)

    def add_square(pos, side, gap):
        side = int(side)
        for x in range(center_x - side//2, center_x + side//2 + 1, gap):
            pos.append([x, center_y - side//2])
            pos.append([x, center_y + side//2])
        for y in range(center_y - side//2, center_y + side//2 + 1, gap):
            pos.append([center_x - side//2, y])
            pos.append([center_x + side//2, y])

    # goal
    pos = []
    add_square(pos, map_size * 0.75, 10)
    add_square(pos, map_size * 0.61, 10)
    add_square(pos, map_size * 0.47, 12)
    add_square(pos, map_size * 0.39, 12)
    env.add_agents(goal_handle, method="custom", pos=pos)

    circle_goal_num = env.get_num(goal_handle)

    def draw(base_x, base_y, scale, data):
        w, h = len(data), len(data[0])
        pos = []
        for i in range(w):
            for j in range(h):
                if data[i][j] == 1:
                    start_x = i * scale + base_y
                    start_y = j * scale + base_x
                    start_x = int(start_x)
                    start_y = int(start_y)
                    for x in range(start_x, start_x + scale):
                        for y in range(start_y, start_y + scale):
                            pos.append([y, x])

        env.add_agents(goal_handle, method="custom", pos=pos)

    base_y = (map_size - len(messages) * font.height) / 2
    for message in messages:
        base_x = (map_size - len(message) * font.width) / 2
        scale = 1
        for x in message:
            data = font.get(x)
            draw(base_x, base_y, scale, data)
            base_x += font.width
        base_y += font.height + 1

    alpha_goal_num = env.get_num(goal_handle) - circle_goal_num

    # agent
    pos = []

    add_square(pos, map_size * 0.95, 1)
    add_square(pos, map_size * 0.9, 1)
    add_square(pos, map_size * 0.85, 1)
    add_square(pos, map_size * 0.80, 1)

    pos = np.array(pos)
    pos = pos[np_random.choice(np.arange(len(pos)), int(circle_goal_num + alpha_goal_num * 1.25), replace=False)]

    env.add_agents(handles[0], method="custom", pos=pos)


class arrange_markov_env(markov_env):
    def __init__(self, map_size, seed):
        env = magent.GridWorld(load_config(map_size=map_size))
        handles = env.get_handles()
        self.np_random, _ = seeding.np_random(seed)

        names = ["red", "blue"]
        super().__init__(env, handles, names, map_size)

    def generate_map(self):
        env, map_size = self.env, self.map_size
        handles = env.get_handles()[1:]
        food_handle = env.get_handles()[0]
        generate_map(env,self.np_random,map_size,food_handle, handles)
