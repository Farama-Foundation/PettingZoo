# noqa: D212, D415
"""
# Waterworld

```{figure} sisl_waterworld.gif
:width: 140px
:name: waterworld
```

This environment is part of the <a href='..'>SISL environments</a>. Please read that page first for general information.

| Import               | `from pettingzoo.sisl import waterworld_v4`            |
|----------------------|--------------------------------------------------------|
| Actions              | Continuous                                             |
| Parallel API         | Yes                                                    |
| Manual Control       | No                                                     |
| Agents               | `agents= ['pursuer_0', 'pursuer_1', ..., 'pursuer_4']` |
| Agents               | 5                                                      |
| Action Shape         | (2,)                                                   |
| Action Values        | [-0.01, 0.01]                                          |
| Observation Shape    | (242,)                                                 |
| Observation Values   | [-√2, 2*√2]                                            |


Waterworld is a simulation of archea navigating and trying to survive in their environment. These archea, called pursuers attempt to consume food while avoiding poison. The agents in waterworld are the pursuers, while food and poison belong to the environment. Poison has a radius which is 0.75
times the size of the pursuer radius, while food has a radius 2 times the size of the pursuer radius. Depending on the input parameters, multiple pursuers may need to work together to consume food, creating a dynamic that is both cooperative and competitive. Similarly, rewards can be distributed
globally to all pursuers, or applied locally to specific pursuers. The environment is a continuous 2D space, and each pursuer has a position with x and y values each in the range [0,1]. Agents can not move beyond barriers at the minimum and maximum x and y values. Agents act by choosing a thrust
vector to add to their current velocity. Each pursuer has a number of evenly spaced sensors which can read the speed and direction of objects near the pursuer. This information is reported in the observation space, and can be used to navigate the environment.

### Observation Space

The observation shape of each agent is a vector of length > 4 that is dependent on the environment's input arguments. The full size of the vector is the number of features per sensor multiplied by the number of sensors, plus two elements indicating whether the pursuer collided with food or with
poison respectively. The number of features per sensor is 8 by default with `speed_features` enabled, or 5 if `speed_features` is turned off. Therefore with `speed_features` enabled, the observation shape takes the full form of `(8 × n_sensors) + 2`. Elements of the observation vector take on
values in the range [-1, 1].

For example, by default there are 5 agents (purple), 5 food targets (red) and 10 poison targets (green). Each agent has 30 range-limited sensors, depicted by the black lines, to detect neighboring entities (food and poison targets) resulting in 242 element vector of computed values about the
environment for the observation space. These values represent the distances and speeds sensed by each sensor on the archea. Sensors that do not sense any objects within their range report 0 for speed and 1 for distance.

This has been fixed from the reference environments to keep items floating off screen and being lost forever.

This table enumerates the observation space with `speed_features = True`:

|        Index: [start, end)         | Description                                  |   Values    |
| :--------------------------------: | -------------------------------------------- | :---------: |
|           0 to n_sensors           | Obstacle distance for each sensor            |   [0, 1]   |
|    n_sensors to (2 * n_sensors)    | Barrier distance for each sensor             |   [0, 1]   |
| (2 * n_sensors) to (3 * n_sensors) | Food distance for each sensor                |   [0, 1]   |
| (3 * n_sensors) to (4 * n_sensors) | Food speed for each sensor                   | [-2*√2, 2*√2] |
| (4 * n_sensors) to (5 * n_sensors) | Poison distance for each sensor              |   [0, 1]   |
| (5 * n_sensors) to (6 * n_sensors) | Poison speed for each sensor                 | [-2*√2, 2*√2] |
| (6 * n_sensors) to (7 * n_sensors) | Pursuer distance for each sensor             |   [0, 1]   |
| (7 * n_sensors) to (8 * n_sensors) | Pursuer speed for each sensor                | [-2*√2, 2*√2] |
|           8 * n_sensors            | Indicates whether agent collided with food   |   {0, 1}    |
|        (8 * n_sensors) + 1         | Indicates whether agent collided with poison |   {0, 1}    |

This table enumerates the observation space with `speed_features = False`:

|        Index: [start, end)        | Description                                  | Values  |
| :-------------------------------: | -------------------------------------------- | :-----: |
|           0 - n_sensors           | Obstacle distance for each sensor            | [0, 1] |
|    n_sensors - (2 * n_sensors)    | Barrier distance for each sensor             | [0, 1] |
| (2 * n_sensors) - (3 * n_sensors) | Food distance for each sensor                | [0, 1] |
| (3 * n_sensors) - (4 * n_sensors) | Poison distance for each sensor              | [0, 1] |
| (4 * n_sensors) - (5 * n_sensors) | Pursuer distance for each sensor             | [0, 1] |
|          (5 * n_sensors)          | Indicates whether agent collided with food   | {0, 1}  |
|        (5 * n_sensors) + 1        | Indicates whether agent collided with poison | {0, 1}  |

### Action Space

The agents have a continuous action space represented as a 2 element vector, which corresponds to horizontal and vertical thrust. The range of values depends on `pursuer_max_accel`.  Action values must be in the range `[-pursuer_max_accel, pursuer_max_accel]`. If the magnitude of this action
vector exceeds `pursuer_max_accel`, it will be scaled down to `pursuer_max_accel`. This velocity vector is added to the archea's current velocity.

**Agent action space:** `[horizontal_thrust, vertical_thrust]`

### Rewards

When multiple agents (depending on `n_coop`) capture food together each agent receives a reward of `food_reward` (the food is not destroyed). They receive a shaping reward of `encounter_reward` for touching food, a reward of `poison_reward` for touching poison, and a `thrust_penalty x ||action||`
reward for every action, where `||action||` is the euclidean norm of the action velocity. All of these rewards are also distributed based on `local_ratio`, where the rewards scaled by `local_ratio` (local rewards) are applied to the agents whose actions produced the rewards, and the rewards
averaged over the number of agents (global rewards) are scaled by `(1 - local_ratio)` and applied to every agent. The environment runs for 500 frames by default.

### Arguments

``` python
waterworld_v4.env(n_pursuers=5, n_evaders=5, n_poisons=10, n_coop=2, n_sensors=20,
sensor_range=0.2,radius=0.015, obstacle_radius=0.2, n_obstacles=1,
obstacle_coord=[(0.5, 0.5)], pursuer_max_accel=0.01, evader_speed=0.01,
poison_speed=0.01, poison_reward=-1.0, food_reward=10.0, encounter_reward=0.01,
thrust_penalty=-0.5, local_ratio=1.0, speed_features=True, max_cycles=500)
```

`n_pursuers`: number of pursuing archea (agents)

`n_evaders`: number of food objects

`n_poisons`: number of poison objects

`n_coop`: number of pursuing archea (agents) that must be touching food at the same time to consume it

`n_sensors`: number of sensors on all pursuing archea (agents)

`sensor_range`: length of sensor dendrite on all pursuing archea (agents)

`radius`: archea base radius. Pursuer: radius, food: 2 x radius, poison: 3/4 x radius

`obstacle_radius`: radius of obstacle object

`obstacle_coord`: coordinate of obstacle object. Can be set to `None` to use a random location

`pursuer_max_accel`: pursuer archea maximum acceleration (maximum action size)

`pursuer_speed`: pursuer (agent) maximum speed

`evader_speed`: food speed

`poison_speed`: poison speed

`poison_reward`: reward for pursuer consuming a poison object (typically negative)

`food_reward`: reward for pursuers consuming a food object

`encounter_reward`: reward for a pursuer colliding with a food object

`thrust_penalty`: scaling factor for the negative reward used to penalize large actions

`local_ratio`: Proportion of reward allocated locally vs distributed globally among all agents

`speed_features`: toggles whether pursuing archea (agent) sensors detect speed of other objects and archea

`max_cycles`: After max_cycles steps all agents will return done

* v4: Major refactor (1.22.0)
* v3: Refactor and major bug fixes (1.5.0)
* v2: Misc bug fixes (1.4.0)
* v1: Various fixes and environment argument changes (1.3.1)
* v0: Initial versions release (1.0.0)

"""

from gymnasium.utils import EzPickle

from pettingzoo import AECEnv
from pettingzoo.sisl.waterworld.waterworld_base import FPS
from pettingzoo.sisl.waterworld.waterworld_base import WaterworldBase as _env
from pettingzoo.utils import agent_selector, wrappers
from pettingzoo.utils.conversions import parallel_wrapper_fn


def env(**kwargs):
    env = raw_env(**kwargs)
    env = wrappers.ClipOutOfBoundsWrapper(env)
    env = wrappers.OrderEnforcingWrapper(env)
    return env


parallel_env = parallel_wrapper_fn(env)


class raw_env(AECEnv, EzPickle):
    metadata = {
        "render_modes": ["human", "rgb_array"],
        "name": "waterworld_v4",
        "is_parallelizable": True,
        "render_fps": FPS,
    }

    def __init__(self, *args, **kwargs):
        EzPickle.__init__(self, *args, **kwargs)
        AECEnv.__init__(self)
        self.env = _env(*args, **kwargs)

        self.agents = ["pursuer_" + str(r) for r in range(self.env.num_agents)]
        self.possible_agents = self.agents[:]
        self.agent_name_mapping = dict(zip(self.agents, list(range(self.num_agents))))
        self._agent_selector = agent_selector(self.agents)

        # spaces
        self.action_spaces = dict(zip(self.agents, self.env.action_space))
        self.observation_spaces = dict(zip(self.agents, self.env.observation_space))
        self.has_reset = False

        self.render_mode = self.env.render_mode

    def observation_space(self, agent):
        return self.observation_spaces[agent]

    def action_space(self, agent):
        return self.action_spaces[agent]

    def convert_to_dict(self, list_of_list):
        return dict(zip(self.agents, list_of_list))

    def reset(self, seed=None, options=None):
        if seed is not None:
            self.env._seed(seed=seed)
        self.has_reset = True
        self.env.reset()
        self.agents = self.possible_agents[:]
        self._agent_selector.reinit(self.agents)
        self.agent_selection = self._agent_selector.next()
        self.rewards = dict(zip(self.agents, [(0) for _ in self.agents]))
        self._cumulative_rewards = dict(zip(self.agents, [(0) for _ in self.agents]))
        self.terminations = dict(zip(self.agents, [False for _ in self.agents]))
        self.truncations = dict(zip(self.agents, [False for _ in self.agents]))
        self.infos = dict(zip(self.agents, [{} for _ in self.agents]))

    def close(self):
        if self.has_reset:
            self.env.close()

    def render(self):
        return self.env.render()

    def step(self, action):
        if (
            self.terminations[self.agent_selection]
            or self.truncations[self.agent_selection]
        ):
            self._was_dead_step(action)
            return

        agent = self.agent_selection
        is_last = self._agent_selector.is_last()
        self.env.step(action, self.agent_name_mapping[agent], is_last)

        for r in self.rewards:
            self.rewards[r] = self.env.control_rewards[self.agent_name_mapping[r]]
        if is_last:
            for r in self.rewards:
                self.rewards[r] += self.env.last_rewards[self.agent_name_mapping[r]]

        if self.env.frames >= self.env.max_cycles:
            self.truncations = dict(zip(self.agents, [True for _ in self.agents]))
        else:
            self.terminations = dict(zip(self.agents, self.env.last_dones))

        self._cumulative_rewards[self.agent_selection] = 0
        self.agent_selection = self._agent_selector.next()
        self._accumulate_rewards()

        if self.render_mode == "human":
            self.render()

    def observe(self, agent):
        return self.env.observe(self.agent_name_mapping[agent])
