import copy
import itertools
import warnings

import gym
import numpy as np

from pettingzoo import AECEnv, ParallelEnv
from pettingzoo.utils import conversions, wrappers
from pettingzoo.utils.agent_selector import agent_selector


def env(**kwargs):
    env = raw_env(**kwargs)
    env = wrappers.AssertOutOfBoundsWrapper(env)
    env = wrappers.OrderEnforcingWrapper(env)
    return env


def raw_env(**kwargs):
    return conversions.parallel_to_aec(parallel_env(**kwargs))


def get_type(agent):
    return agent[: agent.rfind("_")]


class parallel_env(ParallelEnv):

    metadata = {"render.modes": ["human"], "name": "generated_agents_parallel_v0"}

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
        agent_name = f"{type}_{agent_id}"
        self.agents.append(agent_name)
        return agent_name

    def reset(self):
        self.all_dones = {}
        self.agents = []
        self.num_steps = 0
        for i in range(5):
            self.add_agent(self.np_random.choice(self.types))
        return {agent: self.observe(agent) for agent in self.agents}

    def seed(self, seed=None):
        self.np_random, _ = gym.utils.seeding.np_random(seed)

    def step(self, actions):
        done = self.num_steps >= self.max_cycles
        for agent in self.agents:
            assert agent in actions
        all_dones = {agent: done for agent in self.agents}
        if not done:
            for i in range(6):
                if self.np_random.random() < 0.1 and len(self.agents) >= 10:
                    all_dones[self.np_random.choice(self.agents)] = True

            for i in range(3):
                if self.np_random.random() < 0.1:
                    if self.np_random.random() < 0.1:
                        type = self.add_type()
                    else:
                        type = self.np_random.choice(self.types)

                    new_agent = self.add_agent(type)
                    all_dones[new_agent] = False

        all_infos = {agent: {} for agent in self.agents}
        all_rewards = {agent: 0 for agent in self.agents}
        all_rewards[self.np_random.choice(self.agents)] = 1
        all_observes = {agent: self.observe(agent) for agent in self.agents}
        self.agents = [agent for agent in self.agents if not all_dones[agent]]
        return all_observes, all_rewards, all_dones, all_infos

    def render(self, mode="human"):
        print(self.agents)

    def close(self):
        pass
