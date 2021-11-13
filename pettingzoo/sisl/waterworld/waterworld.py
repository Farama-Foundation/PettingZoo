import numpy as np

from pettingzoo import AECEnv
from pettingzoo.utils import agent_selector, wrappers
from pettingzoo.utils.conversions import parallel_wrapper_fn

from .waterworld_base import MAWaterWorld as _env

"""
Waterworld is a simulation of archea navigating and trying to survive in their environment. These archea, called pursuers attempt to consume food while avoiding poison. The agents in waterworld are the pursuers, while food and poison belong to the environment. Poison has a radius which is 0.75 times the size of the pursuer radius, while food has a radius 2 times the size of the pursuer radius. Depending on the input parameters, multiple pursuers may need to work together to consume food, creating a dynamic that is both cooperative and competitive. Similarly, rewards can be distributed globally to all pursuers, or applied locally to specific pursuers. The environment is a continuous 2D space, and each pursuer has a position with x and y values each in the range [0,1]. Agents can not move beyond barriers at the minimum and maximum x and y values. Agents act by choosing a thrust vector to add to their current velocity. Each pursuer has a number of evenly spaced sensors which can read the speed and direction of objects near the pursuer. This information is reported in the observation space, and can be used to navigate the environment.

### Observation Space

This table enumerates the observation space with `speed_features = True`:

|        Index: [start, end)         | Description                                  |   Values    |
| :--------------------------------: | -------------------------------------------- | :---------: |
|           0 to n_sensors           | Obstacle distance for each sensor            |   [0, √2]   |
|    n_sensors to (2 * n_sensors)    | Barrier distance for each sensor             |   [0, √2]   |
| (2 * n_sensors) to (3 * n_sensors) | Food distance for each sensor                |   [0, √2]   |
| (3 * n_sensors) to (4 * n_sensors) | Food speed for each sensor                   | [-√2, 2*√2] |
| (4 * n_sensors) to (5 * n_sensors) | Poison distance for each sensor              |   [0, √2]   |
| (5 * n_sensors) to (6 * n_sensors) | Poison speed for each sensor                 | [-√2, 2*√2] |
| (6 * n_sensors) to (7 * n_sensors) | Pursuer distance for each sensor             |   [0, √2]   |
| (7 * n_sensors) to (8 * n_sensors) | Pursuer speed for each sensor                | [-√2, 2*√2] |
|           8 * n_sensors            | Indicates whether agent collided with food   |   {0, 1}    |
|        (8 * n_sensors) + 1         | Indicates whether agent collided with poison |   {0, 1}    |

This table enumerates the observation space with `speed_features = False`:

|        Index: [start, end)        | Description                                  | Values  |
| :-------------------------------: | -------------------------------------------- | :-----: |
|           0 - n_sensors           | Obstacle distance for each sensor            | [0, √2] |
|    n_sensors - (2 * n_sensors)    | Barrier distance for each sensor             | [0, √2] |
| (2 * n_sensors) - (3 * n_sensors) | Food distance for each sensor                | [0, √2] |
| (3 * n_sensors) - (4 * n_sensors) | Poison distance for each sensor              | [0, √2] |
| (4 * n_sensors) - (5 * n_sensors) | Pursuer distance for each sensor             | [0, √2] |
|          (5 * n_sensors)          | Indicates whether agent collided with food   | {0, 1}  |
|        (5 * n_sensors) + 1        | Indicates whether agent collided with poison | {0, 1}  |

### Action Space

**Agent action space:** `[horizontal_thrust, vertical_thrust]`

### Arguments

`n_pursuers`: number of pursuing archea (agents)

`n_evaders`: number of food objects

`n_poison`: number of poison objects

`n_coop`: number of pursuing archea (agents) that must be touching food at the same time to consume it

`n_sensors`: number of sensors on all pursuing archea (agents)

`sensor_range`: length of sensor dendrite on all pursuing archea (agents)

`radius`: archea base radius. Pursuer: radius, food: 2 x radius, poison: 3/4 x radius

`obstacle_radius`: radius of obstacle object

`obstacle_coord`: coordinate of obstacle object. Can be set to `None` to use a random location

`pursuer_max_accel`: pursuer archea maximum acceleration (maximum action size)

`evader_speed`: food speed

`poison_speed`: poison speed

`poison_reward`: reward for pursuer consuming a poison object (typically negative)

`food_reward`: reward for pursuers consuming a food object

`encounter_reward`: reward for a pursuer colliding with a food object

`thrust_penalty`: scaling factor for the negative reward used to penalize large actions

`local_ratio`: Proportion of reward allocated locally vs distributed globally among all agents

`speed_features`: toggles whether pursuing archea (agent) sensors detect speed of other objects and archea

`max_cycles`: After max_cycles steps all agents will return done
"""

def env(**kwargs):
    env = raw_env(**kwargs)
    env = wrappers.ClipOutOfBoundsWrapper(env)
    env = wrappers.OrderEnforcingWrapper(env)
    return env


parallel_env = parallel_wrapper_fn(env)


class raw_env(AECEnv):

    metadata = {'render.modes': ['human', "rgb_array"], 'name': 'waterworld_v3'}

    def __init__(self, *args, **kwargs):
        super().__init__()
        self.env = _env(*args, **kwargs)

        self.agents = ["pursuer_" + str(r) for r in range(self.env.num_agents)]
        self.possible_agents = self.agents[:]
        self.agent_name_mapping = dict(zip(self.agents, list(range(self.num_agents))))
        self._agent_selector = agent_selector(self.agents)
        # spaces
        self.action_spaces = dict(zip(self.agents, self.env.action_space))
        self.observation_spaces = dict(
            zip(self.agents, self.env.observation_space))
        self.has_reset = False

    def observation_space(self, agent):
        return self.observation_spaces[agent]

    def action_space(self, agent):
        return self.action_spaces[agent]

    def seed(self, seed=None):
        self.env.seed(seed)

    def convert_to_dict(self, list_of_list):
        return dict(zip(self.agents, list_of_list))

    def reset(self):
        self.has_reset = True
        self.env.reset()
        self.agents = self.possible_agents[:]
        self._agent_selector.reinit(self.agents)
        self.agent_selection = self._agent_selector.next()
        self.rewards = dict(zip(self.agents, [(0) for _ in self.agents]))
        self._cumulative_rewards = dict(zip(self.agents, [(0) for _ in self.agents]))
        self.dones = dict(zip(self.agents, [False for _ in self.agents]))
        self.infos = dict(zip(self.agents, [{} for _ in self.agents]))

    def close(self):
        if self.has_reset:
            self.env.close()

    def render(self, mode="human"):
        return self.env.render(mode)

    def step(self, action):
        if self.dones[self.agent_selection]:
            return self._was_done_step(action)
        agent = self.agent_selection

        is_last = self._agent_selector.is_last()
        self.env.step(action, self.agent_name_mapping[agent], is_last)

        for r in self.rewards:
            self.rewards[r] = self.env.control_rewards[self.agent_name_mapping[r]]
        if is_last:
            for r in self.rewards:
                self.rewards[r] += self.env.last_rewards[self.agent_name_mapping[r]]

        if self.env.frames >= self.env.max_cycles:
            self.dones = dict(zip(self.agents, [True for _ in self.agents]))
        else:
            self.dones = dict(zip(self.agents, self.env.last_dones))
        self._cumulative_rewards[self.agent_selection] = 0
        self.agent_selection = self._agent_selector.next()
        self._accumulate_rewards()

    def observe(self, agent):
        return self.env.observe(self.agent_name_mapping[agent])
