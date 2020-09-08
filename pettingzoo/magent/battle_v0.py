from gym.spaces import Discrete, Box
import numpy as np
import warnings
import magent
from pettingzoo import AECEnv
import math
from pettingzoo.magent.render import Renderer
from pettingzoo.utils import agent_selector
from .magent_env import magent_parallel_env, make_env
from pettingzoo.utils._parallel_env import _parallel_env_wrapper
from pettingzoo.utils.to_parallel import parallel_wrapper_fn
from gym.utils import EzPickle


map_size = 45
max_frames_default = 1000


def parallel_env(max_frames=max_frames_default, **reward_args):
    return _parallel_env(map_size, reward_args, max_frames)


def raw_env(max_frames=max_frames_default, **reward_args):
    return _parallel_env_wrapper(_parallel_env(map_size, reward_args, max_frames))


env = make_env(raw_env)


def get_config(map_size, step_reward=-0.005, dead_penalty=-0.1, attack_penalty=-0.1, attack_opponent_reward=0.2):
    gw = magent.gridworld
    cfg = gw.Config()

    cfg.set({"map_width": map_size, "map_height": map_size})
    cfg.set({"minimap_mode": True})
    cfg.set({"embedding_size": 10})

    options = {
        'width': 1, 'length': 1, 'hp': 10, 'speed': 2,
        'view_range': gw.CircleRange(6), 'attack_range': gw.CircleRange(1.5),
        'damage': 2, 'kill_reward': 5, 'step_recover': 0.1,
        'step_reward': step_reward, 'dead_penalty': dead_penalty, 'attack_penalty': attack_penalty
    }
    small = cfg.register_agent_type(
        "small",
        options
    )

    g0 = cfg.add_group(small)
    g1 = cfg.add_group(small)

    a = gw.AgentSymbol(g0, index='any')
    b = gw.AgentSymbol(g1, index='any')

    # reward shaping to encourage attack
    cfg.add_reward_rule(gw.Event(a, 'attack', b), receiver=a, value=attack_opponent_reward)
    cfg.add_reward_rule(gw.Event(b, 'attack', a), receiver=b, value=attack_opponent_reward)

    return cfg


class _parallel_env(magent_parallel_env, EzPickle):
    def __init__(self, map_size, reward_args, max_frames):
        EzPickle.__init__(self, map_size, reward_args, max_frames)
        env = magent.GridWorld(get_config(map_size, **reward_args), map_size=map_size)
        self.leftID = 0
        self.rightID = 1
        names = ["red", "blue"]
        super().__init__(env, env.get_handles(), names, map_size, max_frames)

    def generate_map(self):
        env, map_size, handles = self.env, self.map_size, self.handles
        """ generate a map, which consists of two squares of agents"""
        width = height = map_size
        init_num = map_size * map_size * 0.04
        gap = 3

        self.leftID, self.rightID = self.rightID, self.leftID

        # left
        n = init_num
        side = int(math.sqrt(n)) * 2
        pos = []
        for x in range(width // 2 - gap - side, width // 2 - gap - side + side, 2):
            for y in range((height - side) // 2, (height - side) // 2 + side, 2):
                pos.append([x, y, 0])
        env.add_agents(handles[self.leftID], method="custom", pos=pos)

        # right
        n = init_num
        side = int(math.sqrt(n)) * 2
        pos = []
        for x in range(width // 2 + gap, width // 2 + gap + side, 2):
            for y in range((height - side) // 2, (height - side) // 2 + side, 2):
                pos.append([x, y, 0])
        env.add_agents(handles[self.rightID], method="custom", pos=pos)
