# noqa
"""
# Tiger-Deer

```{figure} magent_tiger_deer.gif
:width: 140px
:name: tiger_deer
```

This environment is part of the <a href='..'>MAgent environments</a>. Please read that page first for general information.

| Import             | `from pettingzoo.magent import tiger_deer_v3` |
|--------------------|-----------------------------------------------|
| Actions            | Discrete                                      |
| Parallel API       | Yes                                           |
| Manual Control     | No                                            |
| Agents             | `agents= [ deer_[0-100], tiger_[0-19] ]`      |
| Agents             | 121                                           |
| Action Shape       | (5),(9)                                       |
| Action Values      | Discrete(5),(9)                               |
| Observation Shape  | (3,3,5), (9,9,5)                              |
| Observation Values | [0,2]                                         |
| State Shape        | (45, 45, 5)                                   |
| State Values       | (0, 2)                                        |

```{figure} ../../_static/img/aec/magent_tiger_deer_aec.svg
:width: 200px
:name: tiger_deer
```

In tiger-deer, there are a number of tigers who are only rewarded for teaming up to take down the deer (two tigers must attack a deer in the same step to receive reward). If they do not eat the deer, they will slowly lose 0.1 HP each turn until they die. If they do eat the deer they regain 8
health (they have 10 health to start). At the same time, the deer are trying to avoid getting attacked. Deer start with 5 HP, lose 1 HP when attacked, and regain 0.1 HP each turn. Deer should run from tigers and tigers should form small teams to take down deer.

### Arguments

``` python
tiger_deer_v3.env(map_size=45, minimap_mode=False, tiger_step_recover=-0.1, deer_attacked=-0.1, max_cycles=500, extra_features=False)
```

`map_size`: Sets dimensions of the (square) map. Increasing the size increases the number of agents.  Minimum size is 10.

`minimap_mode`: Turns on global minimap observations. These observations include your and your opponents piece densities binned over the 2d grid of the observation space. Also includes your `agent_position`, the absolute position on the map (rescaled from 0 to 1).

`tiger_step_recover`: Amount of health a tiger gains/loses per turn (tigers have health 10 and get health 8 from killing a deer)

`deer_attacked`: Reward a deer gets for being attacked

`max_cycles`:  number of frames (a step for each agent) until game terminates

`extra_features`: Adds additional features to observation (see table). Default False

#### Action Space

Key: `move_N` means N separate actions, one to move to each of the N nearest squares on the grid.

Tiger action space: `[do_nothing, move_4, attack_4]`

Deer action space: `[do_nothing, move_4]`

#### Reward

Tiger's reward scheme is:

* 1 reward for attacking a deer alongside another tiger

Deer's reward scheme is:

* -1 reward for dying
* -0.1 for being attacked

#### Observation space

The observation space is a 3x3 map with 5 channels for deer and 9x9 map with 5 channels for tigers, which are (in order):

feature | number of channels
--- | ---
obstacle/off the map| 1
my_team_presence| 1
my_team_hp| 1
other_team_presence| 1
other_team_hp| 1
binary_agent_id(extra_features=True)| 10
one_hot_action(extra_features=True)| 5 Deer/9 Tiger
last_reward(extra_features=True)| 1



### Version History

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

default_map_size = 45
max_cycles_default = 300
minimap_mode_default = False
default_env_args = dict(tiger_step_recover=-0.1, deer_attacked=-0.1)


def parallel_env(
    map_size=default_map_size,
    max_cycles=max_cycles_default,
    minimap_mode=minimap_mode_default,
    extra_features=False,
    render_mode=None,
    **env_args
):
    env_env_args = dict(**default_env_args)
    env_env_args.update(env_args)
    return _parallel_env(
        map_size, minimap_mode, env_env_args, max_cycles, extra_features, render_mode
    )


def raw_env(
    map_size=default_map_size,
    max_cycles=max_cycles_default,
    minimap_mode=minimap_mode_default,
    extra_features=False,
    **env_args
):
    return parallel_to_aec_wrapper(
        parallel_env(map_size, max_cycles, minimap_mode, extra_features, **env_args)
    )


env = make_env(raw_env)


def get_config(map_size, minimap_mode, tiger_step_recover, deer_attacked):
    gw = magent.gridworld
    cfg = gw.Config()

    cfg.set({"map_width": map_size, "map_height": map_size})
    cfg.set({"embedding_size": 10})
    cfg.set({"minimap_mode": minimap_mode})

    options = {
        "width": 1,
        "length": 1,
        "hp": 5,
        "speed": 1,
        "view_range": gw.CircleRange(1),
        "attack_range": gw.CircleRange(0),
        "step_recover": 0.2,
        "kill_supply": 8,
        "dead_penalty": -1.0,
    }

    deer = cfg.register_agent_type("deer", options)

    options = {
        "width": 1,
        "length": 1,
        "hp": 10,
        "speed": 1,
        "view_range": gw.CircleRange(4),
        "attack_range": gw.CircleRange(1),
        "damage": 1,
        "step_recover": tiger_step_recover,
    }
    tiger = cfg.register_agent_type("tiger", options)

    deer_group = cfg.add_group(deer)
    tiger_group = cfg.add_group(tiger)

    a = gw.AgentSymbol(tiger_group, index="any")
    b = gw.AgentSymbol(tiger_group, index="any")
    c = gw.AgentSymbol(deer_group, index="any")

    # tigers get reward when they attack a deer simultaneously
    e1 = gw.Event(a, "attack", c)
    e2 = gw.Event(b, "attack", c)
    tiger_attack_rew = 1
    # reward is halved because the reward is double counted
    cfg.add_reward_rule(
        e1 & e2, receiver=[a, b], value=[tiger_attack_rew / 2, tiger_attack_rew / 2]
    )
    cfg.add_reward_rule(e1, receiver=[c], value=[deer_attacked])

    return cfg


class _parallel_env(magent_parallel_env, EzPickle):
    metadata = {
        "render_modes": ["human", "rgb_array"],
        "name": "tiger_deer_v4",
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
            self,
            map_size,
            minimap_mode,
            reward_args,
            max_cycles,
            extra_features,
            render_mode,
        )
        assert map_size >= 10, "size of map must be at least 10"
        env = magent.GridWorld(
            get_config(map_size, minimap_mode, **reward_args), map_size=map_size
        )

        handles = env.get_handles()
        reward_vals = np.array([1, -1] + list(reward_args.values()))
        reward_range = [
            np.minimum(reward_vals, 0).sum(),
            np.maximum(reward_vals, 0).sum(),
        ]

        names = ["deer", "tiger"]
        super().__init__(
            env,
            handles,
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
        handles = env.get_handles()

        env.add_walls(method="random", n=map_size * map_size * 0.04)
        env.add_agents(handles[0], method="random", n=map_size * map_size * 0.05)
        env.add_agents(handles[1], method="random", n=map_size * map_size * 0.01)
