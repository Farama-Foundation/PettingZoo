from typing import Dict, List, Optional, Union

import numpy as np
from gym import spaces
from gym.utils import EzPickle, seeding

from pettingzoo import AECEnv
from pettingzoo.utils import agent_selector, wrappers

# importing Hanabi and throw error message if pypi package is not installed correctly.
try:
    from hanabi_learning_environment.rl_env import HanabiEnv, make

except ModuleNotFoundError:
    raise ImportError(
        (
            "Hanabi is not installed.\n",
            "Run ´pip3 install hanabi_learning_environment´ from within your project environment.\n",
            "Consult hanabi/README.md for detailed information."
        )
    )
"""
Wrapper class around Deepmind's Hanabi Learning Environment.
"""


class HanabiScorePenalty:
    def __init__(self, env):
        self.env = env

    def __float__(self):
        return -float(self.env.hanabi_env.state.score())


def env(**kwargs):
    env = r_env = raw_env(**kwargs)
    env = wrappers.CaptureStdoutWrapper(env)
    env = wrappers.TerminateIllegalWrapper(env, illegal_reward=HanabiScorePenalty(r_env))
    env = wrappers.AssertOutOfBoundsWrapper(env)
    env = wrappers.OrderEnforcingWrapper(env)
    return env


class raw_env(AECEnv, EzPickle):
    """This class capsules endpoints provided within deepmind/hanabi-learning-environment/rl_env.py."""

    metadata = {
        "render.modes": ["human"],
        "name": "hanabi_v4",
        "is_parallelizable": False,
        "video.frames_per_second": 2,
    }

    # set of all required params
    required_keys: set = {
        'colors',
        'ranks',
        'players',
        'hand_size',
        'max_information_tokens',
        'max_life_tokens',
        'observation_type',
        'random_start_player',
    }

    def __init__(self,
                 colors: int = 5,
                 ranks: int = 5,
                 players: int = 2,
                 hand_size: int = 5,
                 max_information_tokens: int = 8,
                 max_life_tokens: int = 3,
                 observation_type: int = 1,
                 random_start_player: bool = False,
                 ):

        """
        Parameter descriptions :
              - colors: int, Number of colors in [2,5].
              - ranks: int, Number of ranks in [2,5].
              - players: int, Number of players in [2,5].
              - hand_size: int, Hand size in [2,5].
              - max_information_tokens: int, Number of information tokens (>=0).
              - max_life_tokens: int, Number of life tokens (>=1).
              - observation_type: int.
                    0: Minimal observation.
                    1: First-order common knowledge observation.
              - random_start_player: bool, Random start player.

        Common game configurations:
            Hanabi-Full (default) :  {
                "colors": 5,
                "ranks": 5,
                "players": 2,
                "max_information_tokens": 8,
                "max_life_tokens": 3,
                "hand_size": (4 if players >= 4 else 5)
                "observation_type": 1,
                "hand_size": 2
                }

            Hanabi-Small : {
                "colors": 2,
                "ranks": 5,
                "players": 2,
                "max_information_tokens": 3
                "hand_size": 2,
                "max_life_tokens": 1
                "observation_type": 1}

            Hanabi-Very-Small : {
                "colors": 1,
                "ranks": 5,
                "players": 2,
                "max_information_tokens": 3
                "hand_size": 2,
                "max_life_tokens": 1
                "observation_type": 1}

        """
        EzPickle.__init__(
            self,
            colors,
            ranks,
            players,
            hand_size,
            max_information_tokens,
            max_life_tokens,
            observation_type,
            random_start_player,
        )

        # ToDo: Starts
        # Check if all possible dictionary values are within a certain ranges.
        self._raise_error_if_config_values_out_of_range(colors,
                                                        ranks,
                                                        players,
                                                        hand_size,
                                                        max_information_tokens,
                                                        max_life_tokens,
                                                        observation_type,
                                                        random_start_player)

        self._config = {
            'colors': colors,
            'ranks': ranks,
            'players': players,
            'hand_size': hand_size,
            'max_information_tokens': max_information_tokens,
            'max_life_tokens': max_life_tokens,
            'observation_type': observation_type,
            'random_start_player': random_start_player,
        }
        self.hanabi_env: HanabiEnv = HanabiEnv(config=self._config)

        # List of agent names
        self.agents = [f"player_{i}" for i in range(self.hanabi_env.players)]
        self.possible_agents = self.agents[:]

        self.agent_selection: str

        # Sets hanabi game to clean state and updates all internal dictionaries
        self.reset()

        # Set action_spaces and observation_spaces based on params in hanabi_env
        self.action_spaces = {name: spaces.Discrete(self.hanabi_env.num_moves()) for name in self.agents}
        self.observation_spaces = {player_name: spaces.Dict({'observation': spaces.Box(low=0,
                                                                                       high=1,
                                                                                       shape=(
                                                                                        self.hanabi_env.vectorized_observation_shape()[
                                                                                       0],),
                                                                                       dtype=np.float32),
                                                             'action_mask': spaces.Box(low=0, high=1, shape=(
                                                             self.hanabi_env.num_moves(),), dtype=np.int8)})
                                   for player_name in self.agents}

    def observation_space(self, agent):
        return self.observation_spaces[agent]

    def action_space(self, agent):
        return self.action_spaces[agent]

    def seed(self, seed=None):
        config = dict(seed=seed, **self._config)
        self.hanabi_env = HanabiEnv(config=config)

    @staticmethod
    def _raise_error_if_config_values_out_of_range(colors, ranks, players, hand_size, max_information_tokens,
                                                   max_life_tokens, observation_type, random_start_player):

        if not (2 <= colors <= 5):
            raise ValueError(f'Config parameter {colors} is out of bounds. See description in hanabi.py.')

        elif not (2 <= ranks <= 5):
            raise ValueError(f'Config parameter {ranks} is out of bounds. See description in hanabi.py.')

        elif not (2 <= players <= 5):
            raise ValueError(f'Config parameter {players} is out of bounds. See description in hanabi.py.')

        elif not (players <= colors):
            raise ValueError(f'Config parameter colors: {colors} is smaller than players: {players}, which is not allowed. See description in hanabi.py.')

        elif not (2 <= hand_size <= 5):
            raise ValueError(f'Config parameter {hand_size} is out of bounds. See description in hanabi.py.')

        elif not (0 <= max_information_tokens):
            raise ValueError(
                f'Config parameter {max_information_tokens} is out of bounds. See description in hanabi.py.')

        elif not (1 <= max_life_tokens):
            raise ValueError(f'Config parameter {max_life_tokens} is out of bounds. See description in hanabi.py.')

        elif not (0 <= observation_type <= 1):
            raise ValueError(f'Config parameter {observation_type} is out of bounds. See description in hanabi.py.')

    @property
    def observation_vector_dim(self):
        return self.hanabi_env.vectorized_observation_shape()

    @property
    def legal_moves(self) -> List[int]:
        return self.infos[self.agent_selection]['legal_moves']

    @property
    def all_moves(self) -> List[int]:
        return list(range(0, self.hanabi_env.num_moves()))

    # ToDo: Fix Return value
    def reset(self):
        """ Resets the environment for a new game and returns observations of current player as List of ints

        Returns:
            observation: Optional list of integers of length self.observation_vector_dim, describing observations of
            current agent (agent_selection).
        """

        self.agents = self.possible_agents[:]
        # Reset underlying hanabi reinforcement learning environment
        obs = self.hanabi_env.reset()

        # Reset agent and agent_selection
        self._reset_agents(player_number=obs['current_player'])

        self.rewards = {agent: 0 for agent in self.agents}
        self._cumulative_rewards = {name: 0 for name in self.agents}
        # Reset internal state
        self._process_latest_observations(obs=obs)

    def _reset_agents(self, player_number: int):
        """ Rearrange self.agents as pyhanabi starts a different player after each reset(). """

        # Shifts self.agents list as long order starting player is not according to player_number
        while not self.agents[0] == 'player_' + str(player_number):
            self.agents = self.agents[1:] + [self.agents[0]]

        # Agent order list, on which the agent selector operates on.
        self._agent_selector = agent_selector(self.agents)

        # Reset agent_selection
        self.agent_selection = self._agent_selector.reset()

    def _step_agents(self):
        self.agent_selection = self._agent_selector.next()

    def step(self, action: int, observe: bool = True, as_vector: bool = True) -> Optional[Union[np.ndarray,
                                                                                                List[List[dict]]]]:
        """ Advances the environment by one step. Action must be within self.legal_moves, otherwise throws error.

        Returns:
            observation: Optional List of new observations of agent at turn after the action step is performed.
            By default a list of integers, describing the logic state of the game from the view of the agent.
            Can be a returned as a descriptive dictionary, if as_vector=False.
        """
        if self.dones[self.agent_selection]:
            return self._was_done_step(action)
        action = int(action)

        agent_on_turn = self.agent_selection

        if action not in self.legal_moves:
            raise ValueError('Illegal action. Please choose between legal actions, as documented in dict self.infos')

        else:
            # Iterate agent_selection
            self._step_agents()

            # Apply action
            all_observations, reward, done, _ = self.hanabi_env.step(action=action)

            # Update internal state
            self._process_latest_observations(obs=all_observations, reward=reward, done=done)

            # sets current reward for 0 to initialize reward accumulation
            self._cumulative_rewards[agent_on_turn] = 0
            self._accumulate_rewards()

    def observe(self, agent_name: str):
        observation = np.array(self.infos[agent_name]['observations_vectorized'],
                               np.float32) if agent_name in self.infos else np.zeros_like(
            self.observation_spaces[agent_name].low)

        legal_moves = self.infos[agent_name]['legal_moves']
        action_mask = np.zeros(self.hanabi_env.num_moves(), 'int8')
        for i in legal_moves:
            action_mask[i] = 1

        return {'observation': observation, 'action_mask': action_mask}

    def _process_latest_observations(self, obs: Dict, reward: Optional[float] = 0, done: Optional[bool] = False):
        """Updates internal state"""

        self.latest_observations = obs
        self.rewards = {a: reward for a in self.agents}
        self.dones = {player_name: done for player_name in self.agents}

        # Here we have to deal with the player index with offset = 1
        self.infos = {player_name: dict(
            legal_moves=self.latest_observations['player_observations'][int(player_name[-1])]['legal_moves_as_int'],
            # legal_moves_as_dict=self.latest_observations['player_observations'][int(player_name[-1])]['legal_moves'],
            observations_vectorized=self.latest_observations['player_observations'][int(player_name[-1])]['vectorized'],
            # observations=self.latest_observations['player_observations'][int(player_name[-1])
        )
            for player_name in self.agents}

    def render(self, mode='human'):
        """ Supports console print only. Prints player's data.

         Example:
        """
        player_data = self.latest_observations['player_observations']
        print("Active player:", self.possible_agents[player_data[0]['current_player_offset']])
        for i, d in enumerate(player_data):
            print(self.possible_agents[i])
            print("========")
            print(d['pyhanabi'])
            print()

    def close(self):
        pass
