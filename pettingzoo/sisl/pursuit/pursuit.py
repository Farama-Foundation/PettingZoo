import os

import numpy as np
import pygame
from gym.utils import EzPickle

from pettingzoo import AECEnv
from pettingzoo.utils import agent_selector, wrappers
from pettingzoo.utils.conversions import parallel_wrapper_fn

from .manual_control import manual_control
from .pursuit_base import Pursuit as _env

"""
By default 30 blue evader agents and 8 red pursuer agents are placed in a 16 x 16 grid with an obstacle, shown in white, in the center. The evaders move randomly, and the pursuers are controlled. Every time the pursuers fully surround an evader each of the surrounding agents receives a reward of 5 and the evader is removed from the environment. Pursuers also receive a reward of 0.01 every time they touch an evader. The pursuers have a discrete action space of up, down, left, right and stay. Each pursuer observes a 7 x 7 grid centered around itself, depicted by the orange boxes surrounding the red pursuer agents. The environment terminates when every evader has been caught, or when 500 cycles are completed.  Note that this environment has already had the reward pruning optimization described in section 4.1 of the PettingZoo paper applied.

Observation shape takes the full form of `(obs_range, obs_range, 3)` where the first channel is 1s where there is a wall, the second channel indicates the number of allies in each coordinate and the third channel indicates the number of opponents in each coordinate.

### Manual Control

Select different pursuers with 'J' and 'K'. The selected pursuer can be moved with the arrow keys.


### Arguments

:param x_size, y_size: Size of environment world space
:param shared_reward: Whether the rewards should be distributed among all agents
:param n_evaders:  Number of evaders
:param n_pursuers:  Number of pursuers
:param obs_range:  Size of the box around the agent that the agent observes.
:param n_catch:  Number pursuers required around an evader to be considered caught
:param freeze_evaders:  Toggles if evaders can move or not
:param tag_reward:  Reward for 'tagging', or being single evader.
:param term_pursuit:  Reward added when a pursuer or pursuers catch an evader
:param urgency_reward:  Reward to agent added in each step
:param surround:  Toggles whether evader is removed when surrounded, or when n_catch pursuers are on top of evader
:param constraint_window: Size of box (from center, in proportional units) which agents can randomly spawn into the environment world. Default is 1.0, which means they can spawn anywhere on the map. A value of 0 means all agents spawn in the center.
:param max_cycles:  After max_cycles steps all agents will return done
"""

os.environ["PYGAME_HIDE_SUPPORT_PROMPT"] = "hide"


def env(**kwargs):
    env = raw_env(**kwargs)
    env = wrappers.AssertOutOfBoundsWrapper(env)
    env = wrappers.OrderEnforcingWrapper(env)
    return env


parallel_env = parallel_wrapper_fn(env)


class raw_env(AECEnv, EzPickle):

    metadata = {"render.modes": ["human", "rgb_array"], "name": "pursuit_v4"}

    def __init__(self, *args, **kwargs):
        EzPickle.__init__(self, *args, **kwargs)
        self.env = _env(*args, **kwargs)
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

    def seed(self, seed=None):
        self.env.seed(seed)

    def reset(self):
        self.steps = 0
        self.agents = self.possible_agents[:]
        self.rewards = dict(zip(self.agents, [(0) for _ in self.agents]))
        self._cumulative_rewards = dict(zip(self.agents, [(0) for _ in self.agents]))
        self.dones = dict(zip(self.agents, [False for _ in self.agents]))
        self.infos = dict(zip(self.agents, [{} for _ in self.agents]))
        self._agent_selector.reinit(self.agents)
        self.agent_selection = self._agent_selector.next()
        self.env.reset()

    def close(self):
        if not self.closed:
            self.closed = True
            self.env.close()

    def render(self, mode="human"):
        if not self.closed:
            return self.env.render(mode)

    def step(self, action):
        if self.dones[self.agent_selection]:
            return self._was_done_step(action)
        agent = self.agent_selection
        self.env.step(
            action, self.agent_name_mapping[agent], self._agent_selector.is_last()
        )
        for k in self.dones:
            if self.env.frames >= self.env.max_cycles:
                self.dones[k] = True
            else:
                self.dones[k] = self.env.is_terminal
        for k in self.agents:
            self.rewards[k] = self.env.latest_reward_state[self.agent_name_mapping[k]]
        self.steps += 1

        self._cumulative_rewards[self.agent_selection] = 0
        self.agent_selection = self._agent_selector.next()
        self._accumulate_rewards()

    def observe(self, agent):
        o = self.env.safely_observe(self.agent_name_mapping[agent])
        return np.swapaxes(o, 2, 0)

    def observation_space(self, agent: str):
        return self.observation_spaces[agent]

    def action_space(self, agent: str):
        return self.action_spaces[agent]
