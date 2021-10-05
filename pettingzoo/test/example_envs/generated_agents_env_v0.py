import copy
import itertools
import warnings

import gym
import numpy as np

from pettingzoo import AECEnv
from pettingzoo.utils import wrappers
from pettingzoo.utils.agent_selector import agent_selector


def env():
    env = raw_env()
    env = wrappers.AssertOutOfBoundsWrapper(env)
    env = wrappers.OrderEnforcingWrapper(env)
    return env


def get_type(agent):
    return agent[: agent.rfind("_")]


class raw_env(AECEnv):

    metadata = {"render.modes": ["human"], "name": "generated_agents_env_v0"}

    def __init__(self, max_cycles=100):
        super().__init__()
        self._obs_spaces = {}
        self._act_spaces = {}
        self.types = []
        self._agent_counters = {}
        self.max_cycles = max_cycles
        self.seed()
        for i in range(3):
            self.add_type()

    def observation_space(self, agent):
        return self._obs_spaces[get_type(agent)]

    def action_space(self, agent):
        return self._act_spaces[get_type(agent)]

    def observe(self, agent):
        return self.observation_space(agent).sample()

    def add_type(self):
        type_id = len(self.types)
        num_actions = self.np_random.randint(3, 10)
        obs_size = self.np_random.randint(10, 50)
        obs_space = gym.spaces.Box(low=0, high=1, shape=(obs_size,))
        act_space = gym.spaces.Discrete(num_actions)
        new_type = f"type{type_id}"
        self.types.append(new_type)
        self._obs_spaces[new_type] = obs_space
        self._act_spaces[new_type] = act_space
        self._agent_counters[new_type] = 0
        return new_type

    def add_agent(self, type):
        agent_id = self._agent_counters[type]
        self._agent_counters[type] += 1
        agent = f"{type}_{agent_id}"
        self.agents.append(agent)
        self.dones[agent] = False
        self.rewards[agent] = 0
        self._cumulative_rewards[agent] = 0
        self.infos[agent] = {}
        return agent

    def reset(self):
        self.agents = []
        self.rewards = {}
        self._cumulative_rewards = {}
        self.dones = {}
        self.infos = {}
        self.num_steps = 0
        for i in range(5):
            self.add_agent(self.np_random.choice(self.types))

        self._agent_selector = agent_selector(self.agents)
        self.agent_selection = self._agent_selector.reset()

    def seed(self, seed=None):
        self.np_random, _ = gym.utils.seeding.np_random(seed)

    def step(self, action):
        if self.dones[self.agent_selection]:
            return self._was_done_step(action)

        self._clear_rewards()
        self._cumulative_rewards[self.agent_selection] = 0

        if self._agent_selector.is_last():
            for i in range(5):
                if self.np_random.random() < 0.1:
                    if self.np_random.random() < 0.1:
                        type = self.add_type()
                    else:
                        type = self.np_random.choice(self.types)

                    agent = self.add_agent(type)
                    if len(self.agents) >= 20:
                        self.dones[self.np_random.choice(self.agents)] = True

        if self._agent_selector.is_last():
            self.num_steps += 1

        if self.num_steps > self.max_cycles:
            for agent in self.agents:
                self.dones[agent] = True

        self.rewards[self.np_random.choice(self.agents)] = 1

        self._accumulate_rewards()
        self._dones_step_first()

    def render(self, mode="human"):
        print(self.agents)

    def close(self):
        pass
