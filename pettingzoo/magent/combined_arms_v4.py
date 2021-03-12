from gym.spaces import Discrete, Box
import numpy as np
import warnings
import magent
from pettingzoo import AECEnv
import math
from pettingzoo.magent.render import Renderer
from pettingzoo.utils import agent_selector
from .magent_env import magent_parallel_env, make_env
from pettingzoo.utils.conversions import from_parallel_wrapper
from pettingzoo.utils.conversions import parallel_wrapper_fn
from gym.utils import EzPickle


default_map_size = 45
max_cycles_default = 1000
KILL_REWARD = 5
minimap_mode_default = False
default_reward_args = dict(step_reward=-0.005, dead_penalty=-0.1, attack_penalty=-0.1, attack_opponent_reward=0.2)


def parallel_env(map_size=default_map_size, max_cycles=max_cycles_default, minimap_mode=minimap_mode_default, extra_features=False, **reward_args):
    env_reward_args = dict(**default_reward_args)
    env_reward_args.update(reward_args)
    return _parallel_env(map_size, minimap_mode, env_reward_args, max_cycles, extra_features)


def raw_env(map_size=default_map_size, max_cycles=max_cycles_default, minimap_mode=minimap_mode_default, extra_features=False, **reward_args):
    return from_parallel_wrapper(parallel_env(map_size, max_cycles, minimap_mode, extra_features, **reward_args))


env = make_env(raw_env)


def load_config(map_size, minimap_mode, step_reward, dead_penalty, attack_penalty, attack_opponent_reward):
    gw = magent.gridworld
    cfg = gw.Config()

    cfg.set({"map_width": map_size, "map_height": map_size})
    cfg.set({"minimap_mode": minimap_mode})

    cfg.set({"embedding_size": 10})

    options = {
        'width': 1, 'length': 1, 'hp': 10, 'speed': 1,
        'view_range': gw.CircleRange(6), 'attack_range': gw.CircleRange(1),
        'damage': 2, 'step_recover': 0.1, 'attack_in_group': True,
        'step_reward': step_reward, 'dead_penalty': dead_penalty, 'attack_penalty': attack_penalty,
    }

    melee = cfg.register_agent_type(
        "melee",
        options
    )

    options = {
        'width': 1, 'length': 1, 'hp': 3, 'speed': 2,
        'view_range': gw.CircleRange(6), 'attack_range': gw.CircleRange(2),
        'damage': 2, 'step_recover': 0.1, 'attack_in_group': True,
        'step_reward': step_reward, 'dead_penalty': dead_penalty, 'attack_penalty': attack_penalty,
    }

    ranged = cfg.register_agent_type(
        "ranged",
        options
    )

    g0 = cfg.add_group(melee)
    g1 = cfg.add_group(ranged)
    g2 = cfg.add_group(melee)
    g3 = cfg.add_group(ranged)

    arm0_0 = gw.AgentSymbol(g0, index='any')
    arm0_1 = gw.AgentSymbol(g1, index='any')
    arm1_0 = gw.AgentSymbol(g2, index='any')
    arm1_1 = gw.AgentSymbol(g3, index='any')

    # reward shaping
    cfg.add_reward_rule(gw.Event(arm0_0, 'attack', arm1_0), receiver=arm0_0, value=attack_opponent_reward)
    cfg.add_reward_rule(gw.Event(arm0_0, 'attack', arm1_1), receiver=arm0_0, value=attack_opponent_reward)
    cfg.add_reward_rule(gw.Event(arm0_1, 'attack', arm1_0), receiver=arm0_1, value=attack_opponent_reward)
    cfg.add_reward_rule(gw.Event(arm0_1, 'attack', arm1_1), receiver=arm0_1, value=attack_opponent_reward)

    cfg.add_reward_rule(gw.Event(arm1_0, 'attack', arm0_0), receiver=arm1_0, value=attack_opponent_reward)
    cfg.add_reward_rule(gw.Event(arm1_0, 'attack', arm0_1), receiver=arm1_0, value=attack_opponent_reward)
    cfg.add_reward_rule(gw.Event(arm1_1, 'attack', arm0_0), receiver=arm1_1, value=attack_opponent_reward)
    cfg.add_reward_rule(gw.Event(arm1_1, 'attack', arm0_1), receiver=arm1_1, value=attack_opponent_reward)

    # kill reward
    cfg.add_reward_rule(gw.Event(arm0_0, 'kill', arm1_0), receiver=arm0_0, value=KILL_REWARD)
    cfg.add_reward_rule(gw.Event(arm0_0, 'kill', arm1_1), receiver=arm0_0, value=KILL_REWARD)
    cfg.add_reward_rule(gw.Event(arm0_1, 'kill', arm1_0), receiver=arm0_1, value=KILL_REWARD)
    cfg.add_reward_rule(gw.Event(arm0_1, 'kill', arm1_1), receiver=arm0_1, value=KILL_REWARD)

    cfg.add_reward_rule(gw.Event(arm1_0, 'kill', arm0_0), receiver=arm1_0, value=KILL_REWARD)
    cfg.add_reward_rule(gw.Event(arm1_0, 'kill', arm0_1), receiver=arm1_0, value=KILL_REWARD)
    cfg.add_reward_rule(gw.Event(arm1_1, 'kill', arm0_0), receiver=arm1_1, value=KILL_REWARD)
    cfg.add_reward_rule(gw.Event(arm1_1, 'kill', arm0_1), receiver=arm1_1, value=KILL_REWARD)

    return cfg


def generate_map(env, map_size, handles):
    width = map_size
    height = map_size

    init_num = map_size * map_size * 0.04

    gap = 3
    # left
    n = init_num
    side = int(math.sqrt(n)) * 2
    pos = [[], []]
    ct = 0
    for x in range(max(width // 2 - gap - side, 1), width // 2 - gap - side + side, 2):
        for y in range((height - side) // 2, (height - side) // 2 + side, 2):
            pos[ct % 2].append([x, y])
        ct += 1

    xct1 = ct
    for x, y in pos[0] + pos[1]:
        if not (0 < x < width - 1 and 0 < y < height - 1):
            assert False
    env.add_agents(handles[0], method="custom", pos=pos[0])
    env.add_agents(handles[1], method="custom", pos=pos[1])

    # right
    n = init_num
    side = int(math.sqrt(n)) * 2
    pos = [[], []]
    ct = 0
    for x in range(width // 2 + gap, min(width // 2 + gap + side, height - 1), 2):
        for y in range((height - side) // 2, min((height - side) // 2 + side, height - 1), 2):
            pos[ct % 2].append([x, y])
        ct += 1
        if xct1 <= ct:
            break

    for x, y in pos[0] + pos[1]:
        if not (0 < x < width - 1 and 0 < y < height - 1):
            assert False
    env.add_agents(handles[2], method="custom", pos=pos[0])
    env.add_agents(handles[3], method="custom", pos=pos[1])


class _parallel_env(magent_parallel_env, EzPickle):
    metadata = {'render.modes': ['human', 'rgb_array'], 'name': "combined_arms_v4"}

    def __init__(self, map_size, minimap_mode, reward_args, max_cycles, extra_features):
        EzPickle.__init__(self, map_size, minimap_mode, reward_args, max_cycles, extra_features)
        assert map_size >= 16, "size of map must be at least 16"
        env = magent.GridWorld(load_config(map_size, minimap_mode, **reward_args))
        reward_vals = np.array([KILL_REWARD] + list(reward_args.values()))
        reward_range = [np.minimum(reward_vals, 0).sum(), np.maximum(reward_vals, 0).sum()]
        names = ["redmelee", "redranged", "bluemele", "blueranged"]
        super().__init__(env, env.get_handles(), names, map_size, max_cycles, reward_range, minimap_mode, extra_features)

    def generate_map(self):
        generate_map(self.env, self.map_size, self.handles)
