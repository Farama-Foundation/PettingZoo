from gym.spaces import Discrete
import numpy as np
from pettingzoo import AECEnv
from pettingzoo.utils import agent_selector
from pettingzoo.utils import wrappers

rock = 0
paper = 1
scissors = 2
none = 3
MOVES = ["ROCK", "PAPER", "SCISSORS", "None"]
NUM_ITERS = 100


def env():
    env = raw_env()
    env = wrappers.AssertOutOfBoundsWrapper(env)
    env = wrappers.NaNRandomWrapper(env)
    env = wrappers.OrderEnforcingWrapper(env)
    return env


class raw_env(AECEnv):
    """Two-player environment for rock paper scissors.
    The observation is simply the last opponent action."""

    metadata = {'render.modes': ['human']}

    def __init__(self):
        self.num_agents = 2
        self.agents = ["player_" + str(r) for r in range(self.num_agents)]
        self.agent_name_mapping = dict(zip(self.agents, list(range(self.num_agents))))

        self.action_spaces = {agent: Discrete(3) for agent in self.agents}
        self.observation_spaces = {agent: Discrete(4) for agent in self.agents}

        self.display_wait = 0.0
        self.reinit()

    def seed(self, seed=None):
        pass

    def reinit(self):
        self._agent_selector = agent_selector(self.agents)
        self.agent_selection = self._agent_selector.next()
        self.rewards = {agent: 0 for agent in self.agents}
        self.dones = {agent: False for agent in self.agents}
        self.infos = {agent: {} for agent in self.agents}
        self.state = {agent: none for agent in self.agents}
        self.observations = {agent: none for agent in self.agents}
        self.num_moves = 0

    def render(self, mode="human"):
        print("Current state: Agent1: {} , Agent2: {}".format(MOVES[self.state[self.agents[0]]], MOVES[self.state[self.agents[1]]]))

    def observe(self, agent):
        # observation of one agent is the previous state of the other
        return np.array(self.observations[agent])

    def close(self):
        pass

    def reset(self, observe=True):
        self.reinit()
        if observe:
            return self.observe(self.agent_selection)

    def step(self, action, observe=True):
        agent = self.agent_selection

        self.state[self.agent_selection] = action

        # collect reward if it is the last agent to act
        if self._agent_selector.is_last():
            self.rewards[self.agents[0]], self.rewards[self.agents[1]] = {
                (rock, rock): (0, 0),
                (rock, paper): (-1, 1),
                (rock, scissors): (1, -1),
                (paper, rock): (1, -1),
                (paper, paper): (0, 0),
                (paper, scissors): (-1, 1),
                (scissors, rock): (-1, 1),
                (scissors, paper): (1, -1),
                (scissors, scissors): (0, 0),
            }[(self.state[self.agents[0]], self.state[self.agents[1]])]

            self.num_moves += 1
            self.dones = {agent: self.num_moves >= NUM_ITERS for agent in self.agents}

            # observe the current state
            for i in self.agents:
                self.observations[i] = self.state[self.agents[1 - self.agent_name_mapping[i]]]
        else:
            self.state[self.agents[1 - self.agent_name_mapping[agent]]] = none

        self.agent_selection = self._agent_selector.next()
        if observe:
            return self.observe(self.agent_selection)
