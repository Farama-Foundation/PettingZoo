# noqa: D212, D415
"""
# Multiwalker

```{figure} sisl_multiwalker.gif
:width: 140px
:name: multiwalker
```

This environment is part of the <a href='..'>SISL environments</a>. Please read that page first for general information.

| Import               | `from pettingzoo.sisl import multiwalker_v9`   |
|----------------------|------------------------------------------------|
| Actions              | Continuous                                     |
| Parallel API         | Yes                                            |
| Manual Control       | No                                             |
| Agents               | `agents= ['walker_0', 'walker_1', 'walker_2']` |
| Agents               | 3                                              |
| Action Shape         | (4,)                                           |
| Action Values        | (-1, 1)                                        |
| Observation Shape    | (31,)                                          |
| Observation Values   | [-inf,inf]                                     |


In this environment, bipedal robots attempt to carry a package placed on top of them towards the right. By default, the number of robots is set to 3.

Each walker receives a reward equal to the change in position of the package from the previous timestep, multiplied by the `forward_reward` scaling factor. The maximum achievable total reward depends on the terrain length; as a reference, for a terrain length of 75, the total reward under an
optimal policy is around 300.

The environment is done if the package falls, or if the package goes beyond the left edge of the terrain. By default, the environment is also done if any walker falls. In all of these cases, each walker receives a reward of -100. The environment is also done if package falls off the right edge of
the terrain, with reward 0.

When a walker falls, it receives an additional penalty of -10. If `terminate_on_fall = False`, then the environment is not done when the walker falls, but only when the package falls. If `remove_on_fall = True`, the fallen walker is removed from the environment. The agents also receive a small
shaped reward of -5 times the change in their head angle to keep their head oriented horizontally.

If `shared_reward` is chosen (True by default), the agents' individual rewards are averaged to give a single mean reward, which is returned to all agents.

Each walker exerts force on two joints in their two legs, giving a continuous action space represented as a 4 element vector. Each walker observes via a 31 element vector containing simulated noisy lidar data about the environment and information about neighboring walkers. The environment's
duration is capped at 500 frames by default (can be controlled by the `max_cycles` setting).



### Observation Space

Each agent receives an observation composed of various physical properties of its legs and joints, as well as LIDAR readings from the space immediately in front and below the robot. The observation also includes information about neighboring walkers, and the package. The neighbour and package
observations have normally distributed signal noise controlled by `position_noise` and `angle_noise`. For walkers without neighbors, observations about neighbor positions are zero.



This table enumerates the observation space:

| Index: [start, end) | Description                                                  |   Values    |
|:-----------------:|------------------------------------------------------------|:---------------:|
|          0          | Hull angle                |  [0, 2*pi]  |
|          1          | Hull angular velocity                                        | [-inf, inf] |
|          2          | X Velocity                                                   |   [-1, 1]   |
|          3          | Y Velocity                                                   |   [-1, 1]   |
|          4          | Hip joint 1 angle                                            | [-inf, inf] |
|          5          | Hip joint 1 speed                                            | [-inf, inf] |
|          6          | Knee joint 1 angle                                           | [-inf, inf] |
|          7          | Knee joint 1 speed                                           | [-inf, inf] |
|          8          | Leg 1 ground contact flag                                    |   {0, 1}    |
|          9          | Hip joint 1 angle                                            | [-inf, inf] |
|         10          | Hip joint 2 speed                                            | [-inf, inf] |
|         11          | Knee joint 2 angle                                           | [-inf, inf] |
|         12          | Knee joint 2 speed                                           | [-inf, inf] |
|         13          | Leg 2 ground contact flag                                    |   {0, 1}    |
|        14-23        | LIDAR sensor readings                                        | [-inf, inf] |
|         24          | Left neighbor relative X position (0.0 for leftmost walker) (Noisy) | [-inf, inf] |
|         25          | Left neighbor relative Y position (0.0 for leftmost walker) (Noisy) | [-inf, inf] |
|         26          | Right neighbor relative X position (0.0 for rightmost walker) (Noisy) | [-inf, inf] |
|         27          | Right neighbor relative Y position (0.0 for rightmost walker) (Noisy) | [-inf, inf] |
|         28          | Walker X position relative to package (0 for left edge, 1 for right edge) (Noisy) | [-inf, inf] |
|         29          | Walker Y position relative to package (Noisy)                        | [-inf, inf] |
|         30          | Package angle (Noisy)                                                | [-inf, inf] |

### Arguments

``` python
multiwalker_v9.env(n_walkers=3, position_noise=1e-3, angle_noise=1e-3, forward_reward=1.0, terminate_reward=-100.0, fall_reward=-10.0, shared_reward=True,
terminate_on_fall=True, remove_on_fall=True, terrain_length=200, max_cycles=500)
```



`n_walkers`:  number of bipedal walker agents in environment

`position_noise`:  noise applied to neighbors and package positional observations

`angle_noise`:  noise applied to neighbors and package rotational observations

`forward_reward`: reward received is `forward_reward` * change in position of the package

`fall_reward`:  reward applied when an agent falls

`shared_reward`:  whether reward is distributed among all agents or allocated individually

`terminate_reward`: reward applied to each walker if they fail to carry the package to the right edge of the terrain

`terminate_on_fall`: If `True` (default), a single walker falling causes all agents to be done, and they all receive an additional `terminate_reward`. If `False`, then only the fallen agent(s) receive `fall_reward`, and the rest of the agents are not done i.e. the environment continues.

`remove_on_fall`: Remove a walker when it falls (only works when `terminate_on_fall` is False)

`terrain_length`: length of terrain in number of steps

`max_cycles`:  after max_cycles steps all agents will return done


### Version History
* v8: Replaced local_ratio, fixed rewards, terrain length as an argument and documentation (1.15.0)
* v7: Fixed problem with walker collisions (1.8.2)
* v6: Fixed observation space and made large improvements to code quality (1.5.0)
* v5: Fixes to reward structure, added arguments (1.4.2)
* v4: Misc bug fixes (1.4.0)
* v3: Fixes to observation space (1.3.3)
* v2: Various fixes and environment argument changes (1.3.1)
* v1: Fixes to how all environments handle premature death (1.3.0)
* v0: Initial versions release (1.0.0)

"""

import numpy as np
from gymnasium.utils import EzPickle

from pettingzoo import AECEnv
from pettingzoo.sisl.multiwalker.multiwalker_base import FPS
from pettingzoo.sisl.multiwalker.multiwalker_base import MultiWalkerEnv as _env
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
        "name": "multiwalker_v9",
        "is_parallelizable": True,
        "render_fps": FPS,
    }

    def __init__(self, *args, **kwargs):
        EzPickle.__init__(self, *args, **kwargs)
        self.env = _env(*args, **kwargs)
        self.render_mode = self.env.render_mode
        self.agents = ["walker_" + str(r) for r in range(self.env.n_walkers)]
        self.possible_agents = self.agents[:]
        self.agent_name_mapping = dict(
            zip(self.agents, list(range(self.env.n_walkers)))
        )
        self._agent_selector = agent_selector(self.agents)
        # spaces
        self.action_spaces = dict(zip(self.agents, self.env.action_space))
        self.observation_spaces = dict(zip(self.agents, self.env.observation_space))
        self.state_space = self.env.state_space
        self.steps = 0

    def observation_space(self, agent):
        return self.observation_spaces[agent]

    def action_space(self, agent):
        return self.action_spaces[agent]

    def convert_to_dict(self, list_of_list):
        return dict(zip(self.agents, list_of_list))

    def reset(self, seed=None, options=None):
        if seed is not None:
            self.env._seed(seed=seed)
        self.env.reset()
        self.steps = 0
        self.agents = self.possible_agents[:]
        self._agent_selector.reinit(self.agents)
        self.agent_selection = self._agent_selector.next()
        self._cumulative_rewards = dict(zip(self.agents, [(0) for _ in self.agents]))
        self.rewards = dict(zip(self.agents, [(0) for _ in self.agents]))
        self.terminations = dict(zip(self.agents, [False for _ in self.agents]))
        self.truncations = dict(zip(self.agents, [False for _ in self.agents]))
        self.infos = dict(zip(self.agents, [{} for _ in self.agents]))

    def close(self):
        self.env.close()

    def render(self):
        return self.env.render()

    def state(self):
        return self.env.state()

    def observe(self, agent):
        return self.env.observe(self.agent_name_mapping[agent])

    def step(self, action):
        if (
            self.terminations[self.agent_selection]
            or self.truncations[self.agent_selection]
        ):
            self._was_dead_step(action)
            return
        agent = self.agent_selection
        action = np.array(action, dtype=np.float32)
        is_last = self._agent_selector.is_last()
        self.env.step(action, self.agent_name_mapping[agent], is_last)
        if is_last:
            last_rewards = self.env.get_last_rewards()
            for agent in self.rewards:
                self.rewards[agent] = last_rewards[self.agent_name_mapping[agent]]
            for agent in self.terminations:
                self.terminations[agent] = self.env.get_last_dones()[
                    self.agent_name_mapping[agent]
                ]
            self.agent_name_mapping = {
                agent: i
                for i, (agent, done) in enumerate(
                    zip(self.possible_agents, self.env.get_last_dones())
                )
            }
            iter_agents = self.agents[:]
            for agent in self.terminations:
                if self.terminations[agent] or self.truncations[agent]:
                    iter_agents.remove(agent)
            self._agent_selector.reinit(iter_agents)
        else:
            self._clear_rewards()
        if self._agent_selector.agent_order:
            self.agent_selection = self._agent_selector.next()

        if self.env.frames >= self.env.max_cycles:
            self.terminations = dict(zip(self.agents, [True for _ in self.agents]))

        self._cumulative_rewards[agent] = 0
        self._accumulate_rewards()
        self._deads_step_first()
        self.steps += 1

        if self.render_mode == "human":
            self.render()
