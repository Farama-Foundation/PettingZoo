# noqa
"""
# Combined Arms

```{figure} magent_combined_arms.gif
:width: 140px
:name: combined_arms
```

This environment is part of the <a href='..'>MAgent environments</a>. Please read that page first for general information.

| Import             | `from pettingzoo.magent import combined_arms_v6`                                   |
|--------------------|------------------------------------------------------------------------------------|
| Actions            | Discrete                                                                           |
| Parallel API       | Yes                                                                                |
| Manual Control     | No                                                                                 |
| Agents             | `agents= [redmelee_[0-44], redranged_[0-35], bluemelee_[0-44], blueranged_[0-35]]` |
| Agents             | 162                                                                                |
| Action Shape       | (9),(25)                                                                           |
| Action Values      | Discrete(9),(25)                                                                   |
| Observation Shape  | (13,13,9)                                                                          |
| Observation Values | [0,2]                                                                              |
| State Shape        | (45, 45, 9)                                                                        |
| State Values       | (0, 2)                                                                             |

```{figure} ../../_static/img/aec/magent_combined_arms_aec.svg
:width: 200px
:name: combined_arms
```

A large-scale team battle. Here there are two types of agents on each team, ranged units which can attack farther and move faster but have less HP, and melee units which can only attack close units and move more slowly but have more HP. Unlike battle and battlefield, agents can attack units on
their own team (they just are not rewarded for doing so). Agents slowly regain HP over time, so it is best to kill an opposing agent quickly. Specifically, agents have 10 HP, are damaged 2 HP by each attack, and recover 0.1 HP every turn.

### Arguments

``` python
combined_arms_v6.env(map_size=45, minimap_mode=False, step_reward=-0.005,
dead_penalty=-0.1, attack_penalty=-0.1, attack_opponent_reward=0.2, max_cycles=1000,
extra_features=False)
```

`map_size`: Sets dimensions of the (square) map. Increasing the size increases the number of agents. Minimum size is 16.

`minimap_mode`: Turns on global minimap observations. These observations include your and your opponents piece densities binned over the 2d grid of the observation space. Also includes your `agent_position`, the absolute position on the map (rescaled from 0 to 1).


`step_reward`:  reward after every step

`dead_penalty`:  reward when killed

`attack_penalty`:  reward when attacking anything

`attack_opponent_reward`:  reward added for attacking an opponent

`max_cycles`:  number of cycles (a step for each agent) until game terminates

`extra_features`: Adds additional features to observation (see table). Default False

#### Action Space

Key: `move_N` means N separate actions, one to move to each of the N nearest squares on the grid.

Melee action options: `[do_nothing, move_4, attack_4]`

Ranged action options: `[do_nothing, move_12, attack_12]`

#### Reward

Reward is given as:

* 5 reward for killing an opponent
* -0.005 reward every step (step_reward option)
* -0.1 reward for attacking (attack_penalty option)
* 0.2 reward for attacking an opponent (attack_opponent_reward option)
* -0.1 reward for dying (dead_penalty option)

If multiple options apply, rewards are added.

#### Observation space

The observation space is a 13x13 map with the below channels (in order):

feature | number of channels
--- | ---
obstacle/off the map| 1
my_team_presence| 1
my_team_hp| 1
my_team_minimap(minimap_mode=True)| 1
Other teams presences/heaths/minimaps (in some order) | 6 default/9 if minimap_mode=True
binary_agent_id(extra_features=True)| 10
one_hot_action(extra_features=True)| 9 Melee/25 ranged
last_reward(extra_features=True)| 1
agent_position(minimap_mode=True)| 2

### State space

The observation space is a 45x45 map. It contains the following channels, which are (in order):

feature | number of channels
--- | ---
obstacle map | 1
melee_team_1_presence | 1
melee_team_1_hp | 1
ranged_team_1_presence| 1
ranged_team_1_hp | 1
melee_team_2_presence | 1
melee_team_2_hp | 1
ranged_team_2_presence | 1
ranged_team_2_hp | 1
binary_agent_id(extra_features=True)| 10
one_hot_action(extra_features=True)|  25 (max action space)
last_reward(extra_features=True)| 1



### Version History

* v6: Underlying library fix (1.18.0)
* v5: Fixed observation space order (1.9.0)
* v4: Fixed bugs and changed default parameters (1.7.0)
* v3: Added new arguments, fixes to observation space, changes to rewards (1.4.2)
* v2: Observation space bound fix, bumped version of all environments due to adoption of new agent iteration scheme where all agents are iterated over after they are done (1.4.0)
* v1: Agent order under death changed (1.3.0)
* v0: Initial versions release (1.0.0)

"""

import math

import magent
import numpy as np
from gymnasium.utils import EzPickle

from pettingzoo.magent.magent_env import magent_parallel_env, make_env
from pettingzoo.utils.conversions import parallel_to_aec_wrapper

default_map_size = 45
max_cycles_default = 1000
KILL_REWARD = 5
minimap_mode_default = False
default_reward_args = dict(
    step_reward=-0.005,
    dead_penalty=-0.1,
    attack_penalty=-0.1,
    attack_opponent_reward=0.2,
)


def parallel_env(
    map_size=default_map_size,
    max_cycles=max_cycles_default,
    minimap_mode=minimap_mode_default,
    extra_features=False,
    render_mode=None,
    **reward_args
):
    env_reward_args = dict(**default_reward_args)
    env_reward_args.update(reward_args)
    return _parallel_env(
        map_size, minimap_mode, env_reward_args, max_cycles, extra_features, render_mode
    )


def raw_env(
    map_size=default_map_size,
    max_cycles=max_cycles_default,
    minimap_mode=minimap_mode_default,
    extra_features=False,
    render_mode=None,
    **reward_args
):
    return parallel_to_aec_wrapper(
        parallel_env(
            map_size,
            max_cycles,
            minimap_mode,
            extra_features,
            render_mode=render_mode,
            **reward_args
        )
    )


env = make_env(raw_env)


def load_config(
    map_size,
    minimap_mode,
    step_reward,
    dead_penalty,
    attack_penalty,
    attack_opponent_reward,
):
    gw = magent.gridworld
    cfg = gw.Config()

    cfg.set({"map_width": map_size, "map_height": map_size})
    cfg.set({"minimap_mode": minimap_mode})

    cfg.set({"embedding_size": 10})

    options = {
        "width": 1,
        "length": 1,
        "hp": 10,
        "speed": 1,
        "view_range": gw.CircleRange(6),
        "attack_range": gw.CircleRange(1),
        "damage": 2,
        "step_recover": 0.1,
        "attack_in_group": True,
        "step_reward": step_reward,
        "dead_penalty": dead_penalty,
        "attack_penalty": attack_penalty,
    }

    melee = cfg.register_agent_type("melee", options)

    options = {
        "width": 1,
        "length": 1,
        "hp": 3,
        "speed": 2,
        "view_range": gw.CircleRange(6),
        "attack_range": gw.CircleRange(2),
        "damage": 2,
        "step_recover": 0.1,
        "attack_in_group": True,
        "step_reward": step_reward,
        "dead_penalty": dead_penalty,
        "attack_penalty": attack_penalty,
    }

    ranged = cfg.register_agent_type("ranged", options)

    g0 = cfg.add_group(melee)
    g1 = cfg.add_group(ranged)
    g2 = cfg.add_group(melee)
    g3 = cfg.add_group(ranged)

    arm0_0 = gw.AgentSymbol(g0, index="any")
    arm0_1 = gw.AgentSymbol(g1, index="any")
    arm1_0 = gw.AgentSymbol(g2, index="any")
    arm1_1 = gw.AgentSymbol(g3, index="any")

    # reward shaping
    cfg.add_reward_rule(
        gw.Event(arm0_0, "attack", arm1_0),
        receiver=arm0_0,
        value=attack_opponent_reward,
    )
    cfg.add_reward_rule(
        gw.Event(arm0_0, "attack", arm1_1),
        receiver=arm0_0,
        value=attack_opponent_reward,
    )
    cfg.add_reward_rule(
        gw.Event(arm0_1, "attack", arm1_0),
        receiver=arm0_1,
        value=attack_opponent_reward,
    )
    cfg.add_reward_rule(
        gw.Event(arm0_1, "attack", arm1_1),
        receiver=arm0_1,
        value=attack_opponent_reward,
    )

    cfg.add_reward_rule(
        gw.Event(arm1_0, "attack", arm0_0),
        receiver=arm1_0,
        value=attack_opponent_reward,
    )
    cfg.add_reward_rule(
        gw.Event(arm1_0, "attack", arm0_1),
        receiver=arm1_0,
        value=attack_opponent_reward,
    )
    cfg.add_reward_rule(
        gw.Event(arm1_1, "attack", arm0_0),
        receiver=arm1_1,
        value=attack_opponent_reward,
    )
    cfg.add_reward_rule(
        gw.Event(arm1_1, "attack", arm0_1),
        receiver=arm1_1,
        value=attack_opponent_reward,
    )

    # kill reward
    cfg.add_reward_rule(
        gw.Event(arm0_0, "kill", arm1_0), receiver=arm0_0, value=KILL_REWARD
    )
    cfg.add_reward_rule(
        gw.Event(arm0_0, "kill", arm1_1), receiver=arm0_0, value=KILL_REWARD
    )
    cfg.add_reward_rule(
        gw.Event(arm0_1, "kill", arm1_0), receiver=arm0_1, value=KILL_REWARD
    )
    cfg.add_reward_rule(
        gw.Event(arm0_1, "kill", arm1_1), receiver=arm0_1, value=KILL_REWARD
    )

    cfg.add_reward_rule(
        gw.Event(arm1_0, "kill", arm0_0), receiver=arm1_0, value=KILL_REWARD
    )
    cfg.add_reward_rule(
        gw.Event(arm1_0, "kill", arm0_1), receiver=arm1_0, value=KILL_REWARD
    )
    cfg.add_reward_rule(
        gw.Event(arm1_1, "kill", arm0_0), receiver=arm1_1, value=KILL_REWARD
    )
    cfg.add_reward_rule(
        gw.Event(arm1_1, "kill", arm0_1), receiver=arm1_1, value=KILL_REWARD
    )

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
        for y in range(
            (height - side) // 2, min((height - side) // 2 + side, height - 1), 2
        ):
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
    metadata = {
        "render_modes": ["human", "rgb_array"],
        "name": "combined_arms_v6",
        "render_fps": 5,
    }

    def __init__(
        self,
        map_size,
        minimap_mode,
        reward_args,
        max_cycles,
        extra_features,
        render_mode=None,
    ):
        EzPickle.__init__(
            self, map_size, minimap_mode, reward_args, max_cycles, extra_features
        )
        assert map_size >= 16, "size of map must be at least 16"
        env = magent.GridWorld(load_config(map_size, minimap_mode, **reward_args))
        reward_vals = np.array([KILL_REWARD] + list(reward_args.values()))
        reward_range = [
            np.minimum(reward_vals, 0).sum(),
            np.maximum(reward_vals, 0).sum(),
        ]
        names = ["redmelee", "redranged", "bluemele", "blueranged"]
        super().__init__(
            env,
            env.get_handles(),
            names,
            map_size,
            max_cycles,
            reward_range,
            minimap_mode,
            extra_features,
            render_mode,
        )

    def generate_map(self):
        generate_map(self.env, self.map_size, self.handles)
