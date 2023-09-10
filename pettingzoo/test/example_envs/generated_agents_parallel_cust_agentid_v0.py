from typing import Tuple, Union

import gymnasium
import numpy as np
from gymnasium.utils import seeding

from pettingzoo import ParallelEnv
from pettingzoo.utils import conversions, wrappers


def env(**kwargs):
    env = raw_env(**kwargs)
    env = wrappers.AssertOutOfBoundsWrapper(env)
    env = wrappers.OrderEnforcingWrapper(env)
    return env


def raw_env(**kwargs):
    return conversions.parallel_to_aec(parallel_env(**kwargs))


def get_type(agent: Tuple[str, int]):
    return agent[0]


class parallel_env(ParallelEnv[Tuple[str, int], np.ndarray, Union[int, None]]):
    metadata = {"render_modes": ["human"], "name": "generated_agents_parallel_v0"}

    def __init__(self, max_cycles=100, render_mode=None):
        super().__init__()
        self._obs_spaces = {}
        self._act_spaces = {}

        # dummy state space, not actually used
        self.state_space = gymnasium.spaces.MultiDiscrete([10, 10])
        self._state = self.state_space.sample()

        self.types = []
        self._agent_counters = {}
        self.max_cycles = max_cycles
        self.rng_seed = None
        self._seed()
        self.render_mode = render_mode
        for i in range(3):
            self.add_type()

    def observation_space(self, agent):
        return self._obs_spaces[get_type(agent)]

    def action_space(self, agent):
        return self._act_spaces[get_type(agent)]

    def state(self) -> np.ndarray:
        return self._state

    def observe(self, agent):
        return self.observation_space(agent).sample()

    def add_type(self) -> str:
        type_id = len(self.types)
        num_actions = self.np_random.integers(3, 10)
        obs_size = self.np_random.integers(10, 50)
        obs_space = gymnasium.spaces.Box(low=0, high=1, shape=(obs_size,))
        act_space = gymnasium.spaces.Discrete(num_actions)
        obs_space.seed(self.rng_seed)
        act_space.seed(self.rng_seed)
        new_type = f"type{type_id}"
        self.types.append(new_type)
        self._obs_spaces[new_type] = obs_space
        self._act_spaces[new_type] = act_space
        self._agent_counters[new_type] = 0
        return new_type

    def add_agent(self, type: str):
        agent_id = self._agent_counters[type]
        self._agent_counters[type] += 1
        agent_name = (type, agent_id)
        self.agents.append(agent_name)
        return agent_name

    def reset(self, seed=None, options=None):
        self.rng_seed = seed

        if seed is not None:
            self._seed(seed=seed)
        self.num_steps = 0

        # Reset spaces and types
        self._obs_spaces = {}
        self._act_spaces = {}
        self.state_space = gymnasium.spaces.MultiDiscrete([10, 10])
        self._state = self.state_space.sample()

        self.types = []
        self._agent_counters = {}
        for i in range(3):
            self.add_type()

        # Add agents
        self.agents = []
        for i in range(5):
            self.add_agent(self.np_random.choice(self.types))

        # seed observation and action spaces
        for i, agent in enumerate(self.agents):
            self.observation_space(agent).seed(seed)
        for i, agent in enumerate(self.agents):
            self.action_space(agent).seed(seed)

        return {agent: self.observe(agent) for agent in self.agents}, {
            agent: {} for agent in self.agents
        }

    def _seed(self, seed=None):
        self.np_random, _ = seeding.np_random(seed)

    def step(self, actions):
        truncated = self.num_steps >= self.max_cycles
        for agent in self.agents:
            assert agent in actions
        all_truncations = {agent: truncated for agent in self.agents}
        all_terminations = {agent: False for agent in self.agents}
        if not truncated:
            for i in range(6):
                if self.np_random.random() < 0.1 and len(self.agents) >= 10:
                    all_terminations[
                        self.agents[self.np_random.choice(len(self.agents))]
                    ] = True

            for i in range(3):
                if self.np_random.random() < 0.1:
                    if self.np_random.random() < 0.1:
                        type = self.add_type()
                    else:
                        type = self.np_random.choice(self.types)

                    new_agent = self.add_agent(type)
                    all_terminations[new_agent] = False
                    all_truncations[new_agent] = False

        all_infos = {agent: {} for agent in self.agents}
        all_rewards = {agent: 0 for agent in self.agents}
        all_rewards[self.agents[self.np_random.choice(len(self.agents))]] = 1
        all_observes = {agent: self.observe(agent) for agent in self.agents}
        self.agents = [
            agent
            for agent in self.agents
            if not (all_truncations[agent] or all_terminations[agent])
        ]

        if self.render_mode == "human":
            self.render()
        return all_observes, all_rewards, all_terminations, all_truncations, all_infos

    def render(self):
        if self.render_mode is None:
            gymnasium.logger.warn(
                "You are calling render method without specifying any render mode."
            )
        else:
            print(self.agents)

    def close(self):
        pass
