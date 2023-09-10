# noqa: D212, D415
"""
# Pursuit

```{figure} sisl_pursuit.gif
:width: 140px
:name: pursuit
```

This environment is part of the <a href='..'>SISL environments</a>. Please read that page first for general information.

| Import               | `from pettingzoo.sisl import pursuit_v4`               |
|----------------------|--------------------------------------------------------|
| Actions              | Discrete                                               |
| Parallel API         | Yes                                                    |
| Manual Control       | Yes                                                    |
| Agents               | `agents= ['pursuer_0', 'pursuer_1', ..., 'pursuer_7']` |
| Agents               | 8 (+/-)                                                |
| Action Shape         | (5)                                                    |
| Action Values        | Discrete(5)                                            |
| Observation Shape    | (7, 7, 3)                                              |
| Observation Values   | [0, 30]                                                |


By default 30 blue evader agents and 8 red pursuer agents are placed in a 16 x 16 grid with an obstacle, shown in white, in the center. The evaders move randomly, and the pursuers are controlled. Every time the pursuers fully surround an evader each of the surrounding agents receives a reward of 5
and the evader is removed from the environment. Pursuers also receive a reward of 0.01 every time they touch an evader. The pursuers have a discrete action space of up, down, left, right and stay. Each pursuer observes a 7 x 7 grid centered around itself, depicted by the orange boxes surrounding
the red pursuer agents. The environment terminates when every evader has been caught, or when 500 cycles are completed.  Note that this environment has already had the reward pruning optimization described in section 4.1 of the PettingZoo paper applied.

Observation shape takes the full form of `(obs_range, obs_range, 3)` where the first channel is 1s where there is a wall, the second channel indicates the number of allies in each coordinate and the third channel indicates the number of opponents in each coordinate.

### Manual Control

Select different pursuers with 'J' and 'K'. The selected pursuer can be moved with the arrow keys.


### Arguments

``` python
pursuit_v4.env(max_cycles=500, x_size=16, y_size=16, shared_reward=True, n_evaders=30,
n_pursuers=8,obs_range=7, n_catch=2, freeze_evaders=False, tag_reward=0.01,
catch_reward=5.0, urgency_reward=-0.1, surround=True, constraint_window=1.0)
```

`x_size, y_size`: Size of environment world space

`shared_reward`: Whether the rewards should be distributed among all agents

`n_evaders`:  Number of evaders

`n_pursuers`:  Number of pursuers

`obs_range`:  Size of the box around the agent that the agent observes.

`n_catch`:  Number pursuers required around an evader to be considered caught

`freeze_evaders`:  Toggles if evaders can move or not

`tag_reward`:  Reward for 'tagging', or being single evader.

`term_pursuit`:  Reward added when a pursuer or pursuers catch an evader

`urgency_reward`:  Reward to agent added in each step

`surround`:  Toggles whether evader is removed when surrounded, or when n_catch pursuers are on top of evader

`constraint_window`: Size of box (from center, in proportional units) which agents can randomly spawn into the environment world. Default is 1.0, which means they can spawn anywhere on the map. A value of 0 means all agents spawn in the center.

`max_cycles`:  After max_cycles steps all agents will return done


### Version History

* v4: Change the reward sharing, fix a collection bug, add agent counts to the rendering (1.14.0)
* v3: Observation space bug fixed (1.5.0)
* v2: Misc bug fixes (1.4.0)
* v1: Various fixes and environment argument changes (1.3.1)
* v0: Initial versions release (1.0.0)

"""

import numpy as np
import pygame
from gymnasium.utils import EzPickle

from pettingzoo import AECEnv
from pettingzoo.sisl.pursuit.manual_policy import ManualPolicy
from pettingzoo.sisl.pursuit.pursuit_base import Pursuit as _env
from pettingzoo.utils import agent_selector, wrappers
from pettingzoo.utils.conversions import parallel_wrapper_fn

__all__ = ["ManualPolicy", "env", "parallel_env", "raw_env"]


def env(**kwargs):
    env = raw_env(**kwargs)
    env = wrappers.AssertOutOfBoundsWrapper(env)
    env = wrappers.OrderEnforcingWrapper(env)
    return env


parallel_env = parallel_wrapper_fn(env)


class raw_env(AECEnv, EzPickle):
    metadata = {
        "render_modes": ["human", "rgb_array"],
        "name": "pursuit_v4",
        "is_parallelizable": True,
        "render_fps": 5,
        "has_manual_policy": True,
    }

    def __init__(self, *args, **kwargs):
        EzPickle.__init__(self, *args, **kwargs)
        self.env = _env(*args, **kwargs)
        self.render_mode = kwargs.get("render_mode")
        pygame.init()
        self.agents = ["pursuer_" + str(a) for a in range(self.env.num_agents)]
        self.possible_agents = self.agents[:]
        self.agent_name_mapping = dict(zip(self.agents, list(range(self.num_agents))))
        self._agent_selector = agent_selector(self.agents)
        # spaces
        self.n_act_agents = self.env.act_dims[0]
        self.action_spaces = dict(zip(self.agents, self.env.action_space))
        self.observation_spaces = dict(zip(self.agents, self.env.observation_space))
        self.steps = 0
        self.closed = False

    def reset(self, seed=None, options=None):
        if seed is not None:
            self.env._seed(seed=seed)
        self.steps = 0
        self.agents = self.possible_agents[:]
        self.rewards = dict(zip(self.agents, [(0) for _ in self.agents]))
        self._cumulative_rewards = dict(zip(self.agents, [(0) for _ in self.agents]))
        self.terminations = dict(zip(self.agents, [False for _ in self.agents]))
        self.truncations = dict(zip(self.agents, [False for _ in self.agents]))
        self.infos = dict(zip(self.agents, [{} for _ in self.agents]))
        self._agent_selector.reinit(self.agents)
        self.agent_selection = self._agent_selector.next()
        self.env.reset()

    def close(self):
        if not self.closed:
            self.closed = True
            self.env.close()

    def render(self):
        if not self.closed:
            return self.env.render()

    def step(self, action):
        if (
            self.terminations[self.agent_selection]
            or self.truncations[self.agent_selection]
        ):
            self._was_dead_step(action)
            return
        agent = self.agent_selection
        self.env.step(
            action, self.agent_name_mapping[agent], self._agent_selector.is_last()
        )
        for k in self.terminations:
            if self.env.frames >= self.env.max_cycles:
                self.truncations[k] = True
            else:
                self.terminations[k] = self.env.is_terminal
        for k in self.agents:
            self.rewards[k] = self.env.latest_reward_state[self.agent_name_mapping[k]]
        self.steps += 1

        self._cumulative_rewards[self.agent_selection] = 0
        self.agent_selection = self._agent_selector.next()
        self._accumulate_rewards()

        if self.render_mode == "human":
            self.render()

    def observe(self, agent):
        o = self.env.safely_observe(self.agent_name_mapping[agent])
        return np.swapaxes(o, 2, 0)

    def observation_space(self, agent: str):
        return self.observation_spaces[agent]

    def action_space(self, agent: str):
        return self.action_spaces[agent]
