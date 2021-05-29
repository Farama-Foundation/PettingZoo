from typing import Dict, List, Optional, Tuple
from gym.spaces import Discrete
import numpy as np
from pettingzoo import AECEnv
from pettingzoo.utils import agent_selector
from pettingzoo.utils import wrappers
from pettingzoo.utils.conversions import parallel_wrapper_fn

NUM_ITERS: int = 100


def env(moves: List[str], relations: Dict[Tuple[str, str], Tuple[float, float]]) -> AECEnv:
    env = raw_env(moves, relations)
    env = wrappers.CaptureStdoutWrapper(env)
    env = wrappers.AssertOutOfBoundsWrapper(env)
    env = wrappers.OrderEnforcingWrapper(env)
    return env


parallel_env = parallel_wrapper_fn(env)


class raw_env(AECEnv):
    """Two-player environment for generalized version of rock paper scissors.
    The observation is simply the last opponent action."""

    metadata = {'render.modes': ['human'], 'name': 'rps_generalized_v1'}

    def __init__(self, moves: List[str], relations: Dict[Tuple[str, str], Tuple[float, float]]) -> None:
        self.moves: Dict[int, str] = self._parse_moves(moves)
        self.relations: Dict[Tuple[str, str], Tuple[float, float]] = relations
        self.agents: List[str] = ["player_" + str(r) for r in range(2)]
        self.possible_agents: List[str] = self.agents[:]
        self.agent_name_mapping: Dict[str, int] = dict(zip(self.agents, range(self.num_agents)))

        self.action_spaces: Dict[str, Discrete] = {agent: Discrete(self.len_moves) for agent in self.agents}
        self.observation_spaces: Dict[str, Discrete] = {agent: Discrete(self.len_moves + 1) for agent in self.agents}

        self.reinit()

    @property
    def len_moves(self) -> int:
        return len(self.moves)

    @property
    def null_move(self) -> int:
        return self.len_moves

    def _parse_moves(self, moves: List[str]) -> Dict[int, str]:
        assert len(moves) == len(set(moves)), "duplicate elements in moves"
        return dict(zip(range(len(moves)), moves))

    def reinit(self):
        self.agents = self.possible_agents[:]
        self._agent_selector = agent_selector(self.agents)
        self.agent_selection = self._agent_selector.next()
        self.rewards = {agent: 0 for agent in self.agents}
        self._cumulative_rewards = {agent: 0 for agent in self.agents}
        self.dones = {agent: False for agent in self.agents}
        self.infos = {agent: {} for agent in self.agents}
        self.state = {agent: self.null_move for agent in self.agents}
        self.observations = {agent: self.null_move for agent in self.agents}
        self.num_moves = 0

    def move_to_str(self, move: int) -> str:
        return "None" if move == self.null_move else self.moves[move]

    def render(self, mode="human"):
        string = ("Current state: Agent1: {} , Agent2: {}".format(self.move_to_str(self.state[self.agents[0]]), self.move_to_str(self.state[self.agents[1]])))
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
            self.rewards[self.agents[0]], self.rewards[self.agents[1]] = self.relations[
                (self.moves[self.state[self.agents[0]]], self.moves[self.state[self.agents[1]]])
            ]

            self.num_moves += 1
            self.dones = {agent: self.num_moves >= NUM_ITERS for agent in self.agents}

            # observe the current state
            for i in self.agents:
                self.observations[i] = self.state[self.agents[1 - self.agent_name_mapping[i]]]
        else:
            self.state[self.agents[1 - self.agent_name_mapping[agent]]] = self.null_move
            self._clear_rewards()

        self._cumulative_rewards[self.agent_selection] = 0
        self.agent_selection = self._agent_selector.next()
        self._accumulate_rewards()
