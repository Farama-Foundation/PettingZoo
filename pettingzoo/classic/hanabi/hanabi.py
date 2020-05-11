from typing import Optional, Dict, List, Union
import numpy as np
from gym import spaces
from pettingzoo import AECEnv
from pettingzoo.utils import agent_selector, wrappers
from gym.utils import seeding

"""
Wrapper class around google deepmind's hanabi.
"""


def env(**kwargs):
    env = raw_env(**kwargs)
    player_losing_reward = -3
    env = wrappers.TerminateIllegalWrapper(env, illegal_reward=player_losing_reward)
    env = wrappers.AssertOutOfBoundsWrapper(env)
    env = wrappers.NaNRandomWrapper(env)
    env = wrappers.OrderEnforcingWrapper(env)
    return env


class raw_env(AECEnv):
    """This class capsules endpoints provided within deepmind/hanabi-learning-environment/rl_env.py."""

    metadata = {'render.modes': ['human']}

    # set of all required params
    required_keys: set = {
        'colors',
        'ranks',
        'players',
        'hand_size',
        'max_information_tokens',
        'max_life_tokens',
        'observation_type',
        'seed',
        'random_start_player',
    }

    def __init__(self,
                 colors: int = 5,
                 ranks: int = 5,
                 players: int = 2,
                 hand_size: int = 2,
                 max_information_tokens: int = 8,
                 max_life_tokens: int = 3,
                 observation_type: int = 1,
                 seed=None,
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
              - seed: int, Random seed or None.
              - random_start_player: bool, Random start player.

        Common game configurations:
            Hanabi-Full (default) :  {
                "colors": 5,
                "ranks": 5,
                "players": 2,
                "max_information_tokens": 8,
                "max_life_tokens": 3,
                "observation_type": 1,
                "hand_size": 2
                }

            Hanabi-Small : {
                "colors": 5,
                "ranks": 5,
                "players": 2,
                "max_information_tokens":
                "max_life_tokens":
                "observation_type": 1}

            Hanabi-Very-Small : {
                "colors": 2,
                "ranks": 5,
                "players": 2,
                "max_information_tokens":
                "max_life_tokens":
                "observation_type": 1}

        """

        super().__init__()

        seed = seeding.create_seed(seed, max_bytes=3)

        # importing Hanabi and throw error message if pypi package is not installed correctly.
        try:
            from hanabi_learning_environment.rl_env import HanabiEnv, make

        except ModuleNotFoundError:
            print("Hanabi is not installed."
                  + "Run ´pip3 install hanabi_learning_environment´ from within your project environment."
                  + "Consult hanabi/README.md for detailed information.")

        else:

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

            self.hanabi_env: HanabiEnv = HanabiEnv(config={'colors': colors,
                                                           'ranks': ranks,
                                                           'players': players,
                                                           'hand_size': hand_size,
                                                           'max_information_tokens': max_information_tokens,
                                                           'max_life_tokens': max_life_tokens,
                                                           'observation_type': observation_type,
                                                           'random_start_player': random_start_player,
                                                           'seed': seed})

            # List of agent names
            self.agents = ["player_{}".format(i) for i in range(self.hanabi_env.players)]

            self.agent_selection: str

            # Sets hanabi game to clean state and updates all internal dictionaries
            self.reset(observe=False)

            # Set action_spaces and observation_spaces based on params in hanabi_env
            self.action_spaces = {name: spaces.Discrete(self.hanabi_env.num_moves()) for name in self.agents}
            self.observation_spaces = {player_name: spaces.Box(low=0,
                                                               high=1,
                                                               shape=(self.hanabi_env.vectorized_observation_shape()[0],),
                                                               dtype=np.float32)
                                       for player_name in self.agents}

    @staticmethod
    def _raise_error_if_config_values_out_of_range(colors, ranks, players, hand_size, max_information_tokens,
                                                   max_life_tokens, observation_type, random_start_player):

        if not (2 <= colors <= 5):
            raise ValueError(f'Config parameter {colors} is out of bounds. See description in hanabi.py.')

        elif not (2 <= ranks <= 5):
            raise ValueError(f'Config parameter {ranks} is out of bounds. See description in hanabi.py.')

        elif not (2 <= players <= 5):
            raise ValueError(f'Config parameter {players} is out of bounds. See description in hanabi.py.')

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
    def num_agents(self):
        return len(self.agents)

    @property
    def legal_moves(self) -> List[int]:
        return self.infos[self.agent_selection]['legal_moves']

    @property
    def all_moves(self) -> List[int]:
        return list(range(0, self.hanabi_env.num_moves()))

    # ToDo: Fix Return value
    def reset(self, observe=True) -> Optional[List[int]]:
        """ Resets the environment for a new game and returns observations of current player as List of ints

        Returns:
            observation: Optional list of integers of length self.observation_vector_dim, describing observations of
            current agent (agent_selection).
        """

        # Reset underlying hanabi reinforcement learning environment
        obs = self.hanabi_env.reset()

        # Reset agent and agent_selection
        self._reset_agents(player_number=obs['current_player'])

        # Reset internal state
        self._process_latest_observations(obs=obs)

        # If specified, return observation of current agent
        if observe:
            return self.observe(agent_name=self.agent_selection)
        else:
            return None

    def _reset_agents(self, player_number: int):
        """ Rearrange self.agents as pyhanabi starts a different player after each reset(). """

        # Shifts self.agents list as long order starting player is not according to player_number
        while not self.agents[0] == 'player_' + str(player_number):
            self.agents = self.agents[1:] + [self.agents[0]]

        # Agent order list, on which the agent selector operates on.
        self.agent_order = list(self.agents)
        self._agent_selector = agent_selector(self.agent_order)

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

        agent_on_turn = self.agent_selection

        if action not in self.legal_moves:
            raise ValueError(f'Illegal action. Please choose between legal actions, as documented in dict self.infos')

        else:
            # Iterate agent_selection
            self._step_agents()

            # Apply action
            all_observations, reward, done, _ = self.hanabi_env.step(action=action)

            # Update internal state
            self._process_latest_observations(obs=all_observations, reward=reward, done=done)

            # Return latest observations if specified
            if observe:
                return self.observe(agent_name=agent_on_turn)

    def observe(self, agent_name: str):
        return np.array(self.infos[agent_name]['observations_vectorized'], np.float32)


    def _process_latest_observations(self, obs: Dict, reward: Optional[float] = 0, done: Optional[bool] = False):
        """Updates internal state"""

        self.latest_observations = obs
        self.rewards = {player_name: reward for player_name in self.agents}
        self.dones = {player_name: done for player_name in self.agents}

        # Here we have to deal with the player index with offset = 1
        self.infos = {player_name: dict(
                legal_moves=self.latest_observations['player_observations'][int(player_name[-1])]['legal_moves_as_int'],
                legal_moves_as_dict=self.latest_observations['player_observations'][int(player_name[-1])]['legal_moves'],
                observations_vectorized=self.latest_observations['player_observations'][int(player_name[-1])]['vectorized'],
                observations=self.latest_observations['player_observations'][int(player_name[-1])])
              for player_name in self.agents}

    def render(self, mode='human'):
        """ Supports console print only. Prints the whole status dictionary.

         Example:
                     {'current_player': 0,
         'player_observations': [{'current_player': 0,
                            'current_player_offset': 0,
                            'deck_size': 40,
                            'discard_pile': [],
                            'fireworks': {'B': 0,
                                      'G': 0,
                                      'R': 0,
                                      'W': 0,
                                      'Y': 0},
                            'information_tokens': 8,
                            'legal_moves': [{'action_type': 'PLAY',
                                         'card_index': 0},
                                        {'action_type': 'PLAY',
                                         'card_index': 1},
                                        {'action_type': 'PLAY',
                                         'card_index': 2},
                                        {'action_type': 'PLAY',
                                         'card_index': 3},
                                        {'action_type': 'PLAY',
                                         'card_index': 4},
                                        {'action_type': 'REVEAL_COLOR',
                                         'color': 'R',
                                         'target_offset': 1},
                                        {'action_type': 'REVEAL_COLOR',
                                         'color': 'G',
                                         'target_offset': 1},
                                        {'action_type': 'REVEAL_COLOR',
                                         'color': 'B',
                                         'target_offset': 1},
                                        {'action_type': 'REVEAL_RANK',
                                         'rank': 0,
                                         'target_offset': 1},
                                        {'action_type': 'REVEAL_RANK',
                                         'rank': 1,
                                         'target_offset': 1},
                                        {'action_type': 'REVEAL_RANK',
                                         'rank': 2,
                                         'target_offset': 1}],
                            'life_tokens': 3,
                            'observed_hands': [[{'color': None, 'rank': -1},
                                            {'color': None, 'rank': -1},
                                            {'color': None, 'rank': -1},
                                            {'color': None, 'rank': -1},
                                            {'color': None, 'rank': -1}],
                                           [{'color': 'G', 'rank': 2},
                                            {'color': 'R', 'rank': 0},
                                            {'color': 'R', 'rank': 1},
                                            {'color': 'B', 'rank': 0},
                                            {'color': 'R', 'rank': 1}]],
                            'num_players': 2,
                            'vectorized': [ 0, 0, 1, ... ]},
                           {'current_player': 0,
                            'current_player_offset': 1,
                            'deck_size': 40,
                            'discard_pile': [],
                            'fireworks': {'B': 0,
                                      'G': 0,
                                      'R': 0,
                                      'W': 0,
                                      'Y': 0},
                            'information_tokens': 8,
                            'legal_moves': [],
                            'life_tokens': 3,
                            'observed_hands': [[{'color': None, 'rank': -1},
                                            {'color': None, 'rank': -1},
                                            {'color': None, 'rank': -1},
                                            {'color': None, 'rank': -1},
                                            {'color': None, 'rank': -1}],
                                           [{'color': 'W', 'rank': 2},
                                            {'color': 'Y', 'rank': 4},
                                            {'color': 'Y', 'rank': 2},
                                            {'color': 'G', 'rank': 0},
                                            {'color': 'W', 'rank': 1}]],
                            'num_players': 2,
                            'vectorized': [ 0, 0, 1, ... ]}]}
        """
        print(self.latest_observations)

    def close(self):
        pass
