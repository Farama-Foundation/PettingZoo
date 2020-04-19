from typing import Optional, Dict
import numpy as np
from gym import spaces

from pettingzoo import AECEnv

# FixMe: Complete the class documentation
from pettingzoo.utils import agent_selector

"""
The game config, can be specified in two ways:

EITHER:
Specify a config preset by handing in a config string, which is one of:
'Hanabi-Full' | 'Hanabi-Small' | 'Hanabi-Very-Small'

    Hanabi-Full :  {
        "colors": 5, 
        "ranks": 5, 
        "players": 2, 
        "max_information_tokens": 8, 
        "max_life_tokens": 3, 
        "observation_type": 1}
    
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
        
    ADDITIONALLY: You can specify the number of players, when using a preset, by specifying:
     players: int, Number of players \in [2,5].
    

OR: 
Use the following keyword arguments to specify a custom game setup:
    kwargs:
      - colors: int, Number of colors \in [2,5].
      - ranks: int, Number of ranks \in [2,5].
      - players: int, Number of players \in [2,5].
      - hand_size: int, Hand size \in [2,5].
      - max_information_tokens: int, Number of information tokens (>=0).
      - max_life_tokens: int, Number of life tokens (>=1).
      - observation_type: int.
            0: Minimal observation.
            1: First-order common knowledge observation.
      - seed: int, Random seed.
      - random_start_player: bool, Random start player.
"""


class env(AECEnv):

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

    def __init__(self, preset_name: str = None, **kwargs):
        super(env, self).__init__()

        # first try importing pettingZoo and throw error message if submodule is not installed yet.
        try:
            from pettingzoo.classic.hanabi.env.hanabi_learning_environment.rl_env import HanabiEnv, make

        except ModuleNotFoundError:
            print("Hanabi is not installed. Run ´bash pull_prepare_and_setup_hanabi.sh´ from within the hanabi/ dir. " +
                  "Consult hanabi/README.md for detailed information.")

        else:

            # Check if all possible dictionary values are within a certain ranges.
            self._raise_error_if_config_values_out_of_range(kwargs)

            # If a preset name string is provided
            if preset_name is not None:
                # check if players argument is provided
                if 'players' in kwargs.keys():
                    self.hanabi_env: HanabiEnv = make(environment_name=preset_name, num_players={**kwargs}['players'])
                else:
                    self.hanabi_env: HanabiEnv = make(environment_name=preset_name)

            else:
                # check if all required params are provided
                if self.__class__.required_keys.issubset(set(kwargs.keys())):
                    self.hanabi_env: HanabiEnv = HanabiEnv(config=kwargs)
                else:
                    raise KeyError("Incomplete environment configuration provided.")

            self.action_spaces = {name: spaces.Discrete(self.hanabi_env.num_moves()) for name in self.agents}
            self.observation_spaces = {player_name: spaces.Box(low=0,
                                                               high=1,
                                                               shape=(1,
                                                                      1,
                                                                      self.hanabi_env.vectorized_observation_shape()[
                                                                          0]),
                                                               dtype=np.float32)
                                       for player_name in self.agents}

            # Sets hanabi game to clean state and updates all internal dictionaries
            self.reset(observe=False)

            # List of agent names
            self.agents = ["player_{}".format(i) for i in range(self.hanabi_env.players)]

            # Agent order list, on which the agent selector operates on.
            self.agent_order = list(self.agents)
            self._agent_selector = agent_selector(self.agent_order)

            # Set initial agent
            self.agent_selection = self._agent_selector.reset()

    @staticmethod
    def _raise_error_if_config_values_out_of_range(kwargs):
        for key, value in kwargs.items():

            if key == 'colors' and not (2 <= value <= 5):
                raise ValueError(f'Config parameter {key} is out of bounds. See description in hanabi.py.')

            elif key == 'ranks' and not (2 <= value <= 5):
                raise ValueError(f'Config parameter {key} is out of bounds. See description in hanabi.py.')

            elif key == 'players' and not (2 <= value <= 5):
                raise ValueError(f'Config parameter {key} is out of bounds. See description in hanabi.py.')

            elif key == 'hand_size' and not (2 <= value <= 5):
                raise ValueError(f'Config parameter {key} is out of bounds. See description in hanabi.py.')

            elif key == 'max_information_tokens' and not (0 <= value):
                raise ValueError(f'Config parameter {key} is out of bounds. See description in hanabi.py.')

            elif key == 'max_life_tokens' and not (1 <= value):
                raise ValueError(f'Config parameter {key} is out of bounds. See description in hanabi.py.')

            elif key == 'observation_type' and not (0 <= value <= 1):
                raise ValueError(f'Config parameter {key} is out of bounds. See description in hanabi.py.')

    def reset(self, observe=True) -> Optional[Dict]:
        """ Resets the environment for a new game.

        Returns:
            observation: dict, containing the full observation about the game at the
        current step. *WARNING* This observation contains all the hands of the
        players and should not be passed to the agents.
        An example observation:
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
                                                  {'action_type':
                                                  'REVEAL_COLOR',
                                                   'color': 'R',
                                                   'target_offset': 1},
                                                  {'action_type':
                                                  'REVEAL_COLOR',
                                                   'color': 'G',
                                                   'target_offset': 1},
                                                  {'action_type':
                                                  'REVEAL_COLOR',
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
                                  'observed_hands': [[{'color': None, 'rank':
                                  -1},
                                                      {'color': None, 'rank':
                                                      -1},
                                                      {'color': None, 'rank':
                                                      -1},
                                                      {'color': None, 'rank':
                                                      -1},
                                                      {'color': None, 'rank':
                                                      -1}],
                                                     [{'color': 'G', 'rank': 2},
                                                      {'color': 'R', 'rank': 0},
                                                      {'color': 'R', 'rank': 1},
                                                      {'color': 'B', 'rank': 0},
                                                      {'color': 'R', 'rank':
                                                      1}]],
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
                                  'observed_hands': [[{'color': None, 'rank':
                                  -1},
                                                      {'color': None, 'rank':
                                                      -1},
                                                      {'color': None, 'rank':
                                                      -1},
                                                      {'color': None, 'rank':
                                                      -1},
                                                      {'color': None, 'rank':
                                                      -1}],
                                                     [{'color': 'W', 'rank': 2},
                                                      {'color': 'Y', 'rank': 4},
                                                      {'color': 'Y', 'rank': 2},
                                                      {'color': 'G', 'rank': 0},
                                                      {'color': 'W', 'rank':
                                                      1}]],
                                  'num_players': 2,
                                  'vectorized': [ 0, 0, 1, ... ]}]}
        """

        # Reset underlying hanabi reinforcement learning environment
        obs = self.hanabi_env.reset()

        # Update internal state
        self._process_latest_observations(obs=obs)

        # If specified, return observations
        if observe:
            return obs

    # FixMe: Implement this
    def step(self, action: int, observe=True):
        raise NotImplementedError

    # FixMe: Implement this
    def observe(self, agent: str):
        raise NotImplementedError

    # FixMe: Implement this
    def render(self, mode='human'):
        raise NotImplementedError

    # FixMe: Implement this
    def close(self):
        pass

    def _process_latest_observations(self, obs: Dict):
        """Updates internal state"""

        self.latest_observations = obs
        self.rewards = {player_name: 0 for player_name in self.agents}
        self.dones = {player_name: False for player_name in self.agents}
        self.infos = {player_name: dict(legal_moves=self.latest_observations['player_observations']
        [player_index]['legal_moves'], legal_moves_as_int=self.latest_observations['player_observations']
        [player_index]['legal_moves_as_int'], observed_hands=self.latest_observations['player_observations']
        [player_index]['observed_hands'], observed_hands_vectorized=self.latest_observations['player_observations']
        [player_index]['vectorized'])

                      for player_index, player_name in enumerate(self.agents)}
