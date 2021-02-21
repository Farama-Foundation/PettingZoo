from gym.spaces import Discrete
import numpy as np
from pettingzoo import AECEnv
from pettingzoo.utils import agent_selector
from pettingzoo.utils import wrappers

ROCK = 0
PAPER = 1
SCISSORS = 2
LIZARD = 3
SPOCK = 4
NONE = 5
MOVES = ["ROCK", "PAPER", "SCISSORS", "LIZARD", "SPOCK", "None"]
NUM_ITERS = 100


def env():
    env = raw_env()
    env = wrappers.CaptureStdoutWrapper(env)
    env = wrappers.AssertOutOfBoundsWrapper(env)
    env = wrappers.OrderEnforcingWrapper(env)
    return env


class raw_env(AECEnv):
    """Two-player environment for rock paper scissors lizard spock.
    The observation is simply the last opponent action."""

    metadata = {'render.modes': ['human'], "name": "rpsls_v1"}

    def __init__(self):
        self.agents = ["player_" + str(r) for r in range(2)]
        self.possible_agents = self.agents[:]
        self.agent_name_mapping = dict(zip(self.agents, list(range(self.num_agents))))

        self.action_spaces = {agent: Discrete(5) for agent in self.agents}
        self.observation_spaces = {agent: Discrete(6) for agent in self.agents}

        self.reinit()

    def reinit(self):
        self.agents = self.possible_agents[:]
        self._agent_selector = agent_selector(self.agents)
        self.agent_selection = self._agent_selector.next()
        self.rewards = {agent: 0 for agent in self.agents}
        self._cumulative_rewards = {agent: 0 for agent in self.agents}
        self.dones = {agent: False for agent in self.agents}
        self.infos = {agent: {} for agent in self.agents}
        self.state = {agent: NONE for agent in self.agents}
        self.observations = {agent: NONE for agent in self.agents}
        self.num_moves = 0

    def render(self, mode="human"):
        string = ("Current state: Agent1: {} , Agent2: {}".format(MOVES[self.state[self.agents[0]]], MOVES[self.state[self.agents[1]]]))
        print(string)
        return string

    def observe(self, agent):
        # observation of one agent is the previous state of the other
        return np.array(self.observations[agent])

    def close(self):
        pass

    def reset(self):
        self.reinit()

    def step(self, action):
        if self.dones[self.agent_selection]:
            return self._was_done_step(action)
        agent = self.agent_selection

        self.state[self.agent_selection] = action

        # collect reward if it is the last agent to act
        if self._agent_selector.is_last():
            self.rewards[self.agents[0]], self.rewards[self.agents[1]] = {
                (ROCK, ROCK): (0, 0),
                (ROCK, PAPER): (-1, 1),
                (ROCK, SCISSORS): (1, -1),
                (ROCK, LIZARD): (1, -1),
                (ROCK, SPOCK): (-1, 1),

                (PAPER, ROCK): (1, -1),
                (PAPER, PAPER): (0, 0),
                (PAPER, SCISSORS): (-1, 1),
                (PAPER, LIZARD): (-1, 1),
                (PAPER, SPOCK): (1, -1),

                (SCISSORS, ROCK): (-1, 1),
                (SCISSORS, PAPER): (1, -1),
                (SCISSORS, SCISSORS): (0, 0),
                (SCISSORS, LIZARD): (1, -1),
                (SCISSORS, SPOCK): (-1, 1),

                (LIZARD, ROCK): (-1, 1),
                (LIZARD, PAPER): (1, -1),
                (LIZARD, SCISSORS): (-1, 1),
                (LIZARD, LIZARD): (0, 0),
                (LIZARD, SPOCK): (1, -1),

                (SPOCK, ROCK): (1, -1),
                (SPOCK, PAPER): (-1, 1),
                (SPOCK, SCISSORS): (1, -1),
                (SPOCK, LIZARD): (-1, 1),
                (SPOCK, SPOCK): (0, 0),
            }[(self.state[self.agents[0]], self.state[self.agents[1]])]

            self.num_moves += 1
            self.dones = {agent: self.num_moves >= NUM_ITERS for agent in self.agents}

            # observe the current state
            for i in self.agents:
                self.observations[i] = self.state[self.agents[1 - self.agent_name_mapping[i]]]
        else:
            self.state[self.agents[1 - self.agent_name_mapping[agent]]] = NONE
            self._clear_rewards()

        self._cumulative_rewards[self.agent_selection] = 0
        self.agent_selection = self._agent_selector.next()
        self._accumulate_rewards()
