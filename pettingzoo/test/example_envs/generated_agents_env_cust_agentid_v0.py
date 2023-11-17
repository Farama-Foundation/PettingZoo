from typing import Tuple, Union

import gymnasium
import numpy as np

from pettingzoo import AECEnv
from pettingzoo.utils import wrappers
from pettingzoo.utils.agent_selector import agent_selector


def env():
    env = raw_env()
    env = wrappers.AssertOutOfBoundsWrapper(env)
    env = wrappers.OrderEnforcingWrapper(env)
    return env


def get_type(agent: Tuple[str, int]):
    return agent[0]


class raw_env(AECEnv[Tuple[str, int], np.ndarray, Union[int, None]]):
    metadata = {"render_modes": ["human"], "name": "generated_agents_env_v0"}

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
        new_type = f"type{type_id}"
        self.types.append(new_type)
        self._obs_spaces[new_type] = obs_space
        self._act_spaces[new_type] = act_space
        self._agent_counters[new_type] = 0
        return new_type

    def add_agent(self, type):
        agent_id = self._agent_counters[type]
        self._agent_counters[type] += 1
        agent = (type, agent_id)
        self.agents.append(agent)
        self.terminations[agent] = False
        self.truncations[agent] = False
        self.rewards[agent] = 0
        self._cumulative_rewards[agent] = 0
        self.infos[agent] = {}
        return agent

    def reset(self, seed=None, options=None):
        if seed is not None:
            self._seed(seed=seed)
        self.agents = []
        self.rewards = {}
        self._cumulative_rewards = {}
        self.terminations = {}
        self.truncations = {}
        self.infos = {}
        self.num_steps = 0

        self._obs_spaces = {}
        self._act_spaces = {}
        self.state_space = gymnasium.spaces.MultiDiscrete([10, 10])
        self._state = self.state_space.sample()

        self.types = []
        self._agent_counters = {}
        for i in range(3):
            self.add_type()
        for i in range(5):
            self.add_agent(self.np_random.choice(self.types))

        self._agent_selector = agent_selector(self.agents)
        self.agent_selection = self._agent_selector.reset()

        # seed observation and action spaces
        for i, agent in enumerate(self.agents):
            self.observation_space(agent).seed(seed)
        for i, agent in enumerate(self.agents):
            self.action_space(agent).seed(seed)

    def _seed(self, seed=None):
        self.np_random, _ = gymnasium.utils.seeding.np_random(seed)

    def step(self, action):
        if (
            self.terminations[self.agent_selection]
            or self.truncations[self.agent_selection]
        ):
            return self._was_dead_step(action)

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
                        # Randomly terminate one of the agents
                        self.terminations[
                            self.agents[self.np_random.choice(len(self.agents))]
                        ] = True

        if self._agent_selector.is_last():
            self.num_steps += 1

        if self.num_steps > self.max_cycles:
            for agent in self.agents:
                self.truncations[agent] = True

        self.rewards[self.agents[self.np_random.choice(len(self.agents))]] = 1

        self._state = self.state_space.sample()

        self._accumulate_rewards()
        self._deads_step_first()

        # Cycle agents
        self.agent_selection = self._agent_selector.next()

        if self.render_mode == "human":
            self.render()

    def render(self):
        if self.render_mode is None:
            gymnasium.logger.warn(
                "You are calling render method without specifying any render mode."
            )
        else:
            print(self.agents)

    def close(self):
        pass
