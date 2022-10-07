# noqa
"""
# Gather

```{figure} magent_gather.gif
:width: 140px
:name: gather
```

This environment is part of the <a href='..'>MAgent environments</a>. Please read that page first for general information.

| Import             | `from pettingzoo.magent import gather_v4` |
|--------------------|-------------------------------------------|
| Actions            | Discrete                                  |
| Parallel API       | Yes                                       |
| Manual Control     | No                                        |
| Agents             | `agents= [ omnivore_[0-494] ]`            |
| Agents             | 495                                       |
| Action Shape       | (33)                                      |
| Action Values      | Discrete(33)                              |
| Observation Shape  | (15,15,5)                                 |
| Observation Values | [0,2]                                     |
| State Shape        | (200, 200, 5)                             |
| State Values       | (0, 2)                                    |

```{figure} ../../_static/img/aec/magent_gather_aec.svg
:width: 200px
:name: gather
```

In gather, the agents gain reward by eating food. Food needs to be broken down by 5 "attacks" before it is absorbed. Since there is finite food on the map, there is competitive pressure between agents over the food. You expect to see that agents coordinate by not attacking each other until food is
scarce. When food is scarce, agents may attack each other to try to monopolize the food. Agents can kill each other with a single attack.

### Arguments

``` python
gather_v4.env(minimap_mode=False, step_reward=-0.01, attack_penalty=-0.1,
dead_penalty=-1, attack_food_reward=0.5, max_cycles=500, extra_features=False)
```

`minimap_mode`: Turns on global minimap observations. These observations include your and your opponents piece densities binned over the 2d grid of the observation space. Also includes your `agent_position`, the absolute position on the map (rescaled from 0 to 1).

`step_reward`:  reward added unconditionally

`dead_penalty`:  reward added when killed

`attack_penalty`:  reward added for attacking

`attack_food_reward`:  Reward added for attacking a food

`max_cycles`:  number of frames (a step for each agent) until game terminates

`extra_features`: Adds additional features to observation (see table). Default False

#### Action Space

Key: `move_N` means N separate actions, one to move to each of the N nearest squares on the grid.

Action options: `[do_nothing, move_28, attack_4]`

#### Reward

Reward is given as:

* 5 reward for eating a food (requires multiple attacks)
* -0.01 reward every step (step_reward option)
* -0.1 reward for attacking (attack_penalty option)
* -1 reward for dying (dead_penalty option)
* 0.5 reward for attacking a food (attack_food_reward option)

#### Observation space

The observation space is a 15x15 map with the below channels (in order):

feature | number of channels
--- | ---
obstacle/off the map| 1
omnivore_presence| 1
omnivore_hp| 1
omnivore_minimap(minimap_mode=True)| 1
food_presense| 1
food_hp| 1
food_minimap(minimap_mode=True)| 1
one_hot_action(extra_features=True)| 33
last_reward(extra_features=True)| 1
agent_position(minimap_mode=True)| 2

### State space

The observation space is a 200x200 map. It contains the following channels, which are (in order):

feature | number of channels
--- | ---
obstacle map| 1
omnivore_presence| 1
omnivore_hp| 1
food_presence| 1
food_hp| 1
one_hot_action(extra_features=True)|  33 (max action space)
last_reward(extra_features=True)| 1



### Version History

* v4: Underlying library fix (1.18.0)
* v3: Fixed bugs and changed default parameters (1.7.0)
* v2: Observation space bound fix, bumped version of all environments due to adoption of new agent iteration scheme where all agents are iterated over after they are done (1.4.0)
* v1: Agent order under death changed (1.3.0)
* v0: Initial versions release (1.0.0)

"""

import magent
import numpy as np
from gymnasium.utils import EzPickle

from pettingzoo.magent.magent_env import magent_parallel_env, make_env
from pettingzoo.utils.conversions import parallel_to_aec_wrapper

map_size = 200
max_cycles_default = 500
KILL_REWARD = 5
minimap_mode_default = False
default_reward_args = dict(
    step_reward=-0.01, attack_penalty=-0.1, dead_penalty=-1, attack_food_reward=0.5
)


def parallel_env(
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
    max_cycles=max_cycles_default,
    minimap_mode=minimap_mode_default,
    extra_features=False,
    **reward_args
):
    return parallel_to_aec_wrapper(
        parallel_env(max_cycles, minimap_mode, extra_features, **reward_args)
    )


env = make_env(raw_env)


def load_config(
    size, minimap_mode, step_reward, attack_penalty, dead_penalty, attack_food_reward
):
    gw = magent.gridworld
    cfg = gw.Config()

    cfg.set({"map_width": size, "map_height": size})
    cfg.set({"minimap_mode": minimap_mode})

    options = {
        "width": 1,
        "length": 1,
        "hp": 3,
        "speed": 3,
        "view_range": gw.CircleRange(7),
        "attack_range": gw.CircleRange(1),
        "damage": 6,
        "step_recover": 0,
        "attack_in_group": 1,
        "step_reward": step_reward,
        "attack_penalty": attack_penalty,
        "dead_penalty": dead_penalty,
    }

    agent = cfg.register_agent_type(name="agent", attr=options)

    options = {
        "width": 1,
        "length": 1,
        "hp": 25,
        "speed": 0,
        "view_range": gw.CircleRange(1),
        "attack_range": gw.CircleRange(0),
        "kill_reward": KILL_REWARD,
    }
    food = cfg.register_agent_type(name="food", attr=options)

    g_f = cfg.add_group(food)
    g_s = cfg.add_group(agent)

    a = gw.AgentSymbol(g_s, index="any")
    b = gw.AgentSymbol(g_f, index="any")

    cfg.add_reward_rule(gw.Event(a, "attack", b), receiver=a, value=attack_food_reward)

    return cfg


class _parallel_env(magent_parallel_env, EzPickle):
    metadata = {
        "render_modes": ["human", "rgb_array"],
        "name": "gather_v5",
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
        env = magent.GridWorld(load_config(map_size, minimap_mode, **reward_args))
        handles = env.get_handles()
        reward_vals = np.array([5] + list(reward_args.values()))
        reward_range = [
            np.minimum(reward_vals, 0).sum(),
            np.maximum(reward_vals, 0).sum(),
        ]
        names = ["omnivore"]
        super().__init__(
            env,
            handles[1:],
            names,
            map_size,
            max_cycles,
            reward_range,
            minimap_mode,
            extra_features,
            render_mode,
        )

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

        # pattern
        pattern = [
            [
                int(not ((i % 4 == 0 or i % 4 == 1) or (j % 4 == 0 or j % 4 == 1)))
                for j in range(53)
            ]
            for i in range(53)
        ]

        def draw(base_x, base_y, data):
            w, h = len(data), len(data[0])
            pos = []
            for i in range(w):
                for j in range(h):
                    if data[i][j] == 1:
                        start_x = i + base_x
                        start_y = j + base_y
                        for x in range(start_x, start_x + 1):
                            for y in range(start_y, start_y + 1):
                                pos.append([y, x])

            env.add_agents(food_handle, method="custom", pos=pos)

        w, h = len(pattern), len(pattern[0])

        draw(map_size // 2 - w // 2, map_size // 2 - h // 2, pattern)
