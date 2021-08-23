from gym.spaces import Discrete, Box
import numpy as np
import warnings
import magent
from pettingzoo import AECEnv
import math
from pettingzoo.magent.render import Renderer
from pettingzoo.utils import agent_selector
from .magent_env import magent_parallel_env, make_env
from pettingzoo.utils.conversions import parallel_wrapper_fn
from pettingzoo.utils.conversions import from_parallel_wrapper
from gym.utils import EzPickle


map_size = 200
max_cycles_default = 500
KILL_REWARD = 5
minimap_mode_default = False
default_reward_args = dict(step_reward=-0.01, attack_penalty=-0.1, dead_penalty=-1, attack_food_reward=0.5)


def parallel_env(max_cycles=max_cycles_default, minimap_mode=minimap_mode_default, extra_features=False, **reward_args):
    env_reward_args = dict(**default_reward_args)
    env_reward_args.update(reward_args)
    return _parallel_env(map_size, minimap_mode, env_reward_args, max_cycles, extra_features)


def raw_env(max_cycles=max_cycles_default, minimap_mode=minimap_mode_default, extra_features=False, **reward_args):
    return from_parallel_wrapper(parallel_env(max_cycles, minimap_mode, extra_features, **reward_args))


env = make_env(raw_env)


def load_config(size, minimap_mode, step_reward, attack_penalty, dead_penalty, attack_food_reward):
    gw = magent.gridworld
    cfg = gw.Config()

    cfg.set({"map_width": size, "map_height": size})
    cfg.set({"minimap_mode": minimap_mode})

    options = {
        'width': 1, 'length': 1, 'hp': 3, 'speed': 3,
        'view_range': gw.CircleRange(7), 'attack_range': gw.CircleRange(1),
        'damage': 6, 'step_recover': 0, 'attack_in_group': 1,
        'step_reward': step_reward, 'attack_penalty': attack_penalty, 'dead_penalty': dead_penalty
    }

    agent = cfg.register_agent_type(
        name="agent",
        attr=options)

    options = {
        'width': 1, 'length': 1, 'hp': 25, 'speed': 0,
        'view_range': gw.CircleRange(1), 'attack_range': gw.CircleRange(0),
        'kill_reward': KILL_REWARD}
    food = cfg.register_agent_type(
        name='food',
        attr=options)

    g_f = cfg.add_group(food)
    g_s = cfg.add_group(agent)

    a = gw.AgentSymbol(g_s, index='any')
    b = gw.AgentSymbol(g_f, index='any')

    cfg.add_reward_rule(gw.Event(a, 'attack', b), receiver=a, value=attack_food_reward)

    return cfg


class _parallel_env(magent_parallel_env, EzPickle):
    metadata = {'render.modes': ['human', 'rgb_array'], 'name': "gather_v3"}

    def __init__(self, map_size, minimap_mode, reward_args, max_cycles, extra_features):
        EzPickle.__init__(self, map_size, minimap_mode, reward_args, max_cycles, extra_features)
        env = magent.GridWorld(load_config(map_size, minimap_mode, **reward_args))
        handles = env.get_handles()
        reward_vals = np.array([5] + list(reward_args.values()))
        reward_range = [np.minimum(reward_vals, 0).sum(), np.maximum(reward_vals, 0).sum()]
        names = ["omnivore"]
        super().__init__(env, handles[1:], names, map_size, max_cycles, reward_range, minimap_mode, extra_features)

    def generate_map(self):
        env, map_size = self.env, self.map_size
        handles = env.get_handles()[1:]
        food_handle = env.get_handles()[0]
        center_x, center_y = map_size // 2, map_size // 2

        def add_square(pos, side, gap):
            side = int(side)
            for x in range(center_x - side // 2, center_x + side // 2 + 1, gap):
                pos.append([x, center_y - side // 2])
                pos.append([x, center_y + side // 2])
            for y in range(center_y - side // 2, center_y + side // 2 + 1, gap):
                pos.append([center_x - side // 2, y])
                pos.append([center_x + side // 2, y])

        # agent
        pos = []
        add_square(pos, map_size * 0.9, 3)
        add_square(pos, map_size * 0.8, 4)
        add_square(pos, map_size * 0.7, 6)
        env.add_agents(handles[0], method="custom", pos=pos)

        # food
        pos = []
        add_square(pos, map_size * 0.65, 10)
        add_square(pos, map_size * 0.6, 10)
        add_square(pos, map_size * 0.55, 10)
        add_square(pos, map_size * 0.5, 4)
        add_square(pos, map_size * 0.45, 3)
        add_square(pos, map_size * 0.4, 1)
        add_square(pos, map_size * 0.3, 1)
        add_square(pos, map_size * 0.3 - 2, 1)
        add_square(pos, map_size * 0.3 - 4, 1)
        add_square(pos, map_size * 0.3 - 6, 1)
        env.add_agents(food_handle, method="custom", pos=pos)

        # legend
        legend = [
            [1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [1, 0, 1, 1, 1, 1, 1, 0, 1, 0, 0, 0, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 0, 0, 0],
            [1, 0, 0, 1, 1, 1, 0, 0, 1, 0, 0, 1, 1, 0, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 0, 0, 0],
            [1, 0, 0, 0, 1, 0, 0, 0, 1, 0, 1, 1, 0, 0, 0, 1, 1, 0, 0, 1, 1, 1, 1, 1, 0, 0, 0, 1, 1, 1, 1, 1, 0, 0, 1, 1, 1, 1, 1, 0, 0, 1, 1, 1, 1, 0, 0],
            [1, 0, 0, 0, 0, 0, 0, 0, 1, 0, 1, 1, 0, 0, 0, 1, 1, 0, 1, 1, 0, 0, 0, 1, 1, 0, 1, 1, 0, 0, 0, 1, 1, 0, 1, 1, 0, 0, 1, 1, 0, 0, 1, 1, 0, 0, 0],
            [1, 0, 0, 1, 0, 1, 0, 0, 1, 0, 1, 1, 1, 1, 1, 1, 1, 0, 1, 1, 0, 0, 0, 1, 1, 0, 1, 1, 1, 1, 1, 1, 1, 0, 1, 1, 0, 0, 1, 1, 0, 0, 1, 1, 0, 0, 0],
            [1, 0, 0, 1, 1, 1, 0, 0, 1, 0, 1, 1, 0, 0, 0, 1, 1, 0, 1, 1, 0, 0, 0, 1, 1, 0, 1, 1, 0, 0, 0, 0, 0, 0, 1, 1, 0, 0, 1, 1, 0, 0, 1, 1, 0, 0, 0],
            [1, 0, 0, 1, 1, 1, 0, 0, 1, 0, 1, 1, 0, 0, 0, 1, 1, 0, 0, 1, 1, 1, 1, 1, 1, 0, 0, 1, 1, 1, 1, 1, 0, 0, 1, 1, 0, 0, 1, 1, 0, 0, 0, 1, 1, 1, 0],
            [1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        ]

        org = [
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 0, 0, 1, 1, 1, 0, 0, 0, 1, 1, 1, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 0, 1, 1, 1, 0, 0, 1, 1, 1, 1, 1, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 1, 0, 0, 0, 1, 0, 1, 0, 0, 0, 1, 0, 1, 0, 0, 1, 0, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 1, 1, 1, 0, 1, 1, 1, 1, 1, 0, 1, 1, 1, 1, 1, 0, 1, 1, 1, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 0, 0, 0, 1, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 1, 0, 1, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 1, 0, 0, 1, 0, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 0, 0, 0, 1, 1, 1, 0, 0, 0, 1, 1, 1, 0, 0, 1, 0, 0, 0, 1, 0, 1, 0, 1, 0, 0, 0, 1, 0, 1, 1, 1, 1, 1, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        ]

        def draw(base_x, base_y, scale, data):
            w, h = len(data), len(data[0])
            pos = []
            for i in range(w):
                for j in range(h):
                    if data[i][j] == 1:
                        start_x = i * scale + base_x
                        start_y = j * scale + base_y
                        for x in range(start_x, start_x + scale):
                            for y in range(start_y, start_y + scale):
                                pos.append([y, x])

            env.add_agents(food_handle, method="custom", pos=pos)

        scale = 1
        w, h = len(legend), len(legend[0])
        offset = -3
        draw(offset + map_size // 2 - w // 2 * scale, map_size // 2 - h // 2 * scale, scale, legend)
        draw(offset + map_size // 2 - w // 2 * scale + len(legend), map_size // 2 - h // 2 * scale, scale, org)
