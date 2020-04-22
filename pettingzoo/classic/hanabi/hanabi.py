from typing import Optional, Dict, List, Union
import numpy as np
from gym import spaces
from pettingzoo import AECEnv
from pettingzoo.utils import agent_selector

"""
This wrapper is directly based on their git repository and requires
it to be downloaded and installed via git submodule to operate.
For full information see README.md.
"""


class env(AECEnv):
    """This class capsules endpoints provided within deepmind/hanabi-learning-environment/rl_env.py."""

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
        """
        Game configuration for an environment instance can be specified in two ways:

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

        super(env, self).__init__()

        # try importing Hanabi and throw error message if git submodule is not installed yet.
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

            # List of agent names
            self.agents = ["player_{}".format(i) for i in range(self.hanabi_env.players)]

            self.agent_selection: str

            # Sets hanabi game to clean state and updates all internal dictionaries
            self.reset(observe=False)

            # Set action_spaces and observation_spaces based on params in hanabi_env
            self.action_spaces = {name: spaces.Discrete(self.hanabi_env.num_moves()) for name in self.agents}
            self.observation_spaces = {player_name: spaces.Box(low=0,
                                                               high=1,
                                                               shape=(1,
                                                                      1,
                                                                      self.hanabi_env.vectorized_observation_shape()[
                                                                          0]),
                                                               dtype=np.float32)
                                       for player_name in self.agents}

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
                return self.observe(agent_name=agent_on_turn, as_vector=as_vector)

    def observe(self, agent_name: str, as_vector: bool = True) -> Union[np.ndarray, List]:
        if as_vector:
            return np.array([[self.infos[agent_name]['observations_vectorized']]], np.int32)
        else:
            return self.infos[agent_name]['observations']

    def render(self, mode='human'):
        """ Prints the whole status dictionary """
        print(self.latest_observations)

    def close(self):
        pass

    def _process_latest_observations(self, obs: Dict, reward: Optional[float] = 0, done: Optional[bool] = False):
        """Updates internal state"""

        self.latest_observations = obs
        self.rewards = {player_name: reward for player_name in self.agents}
        self.dones = {player_name: done for player_name in self.agents}

        # Here we have to deal with the player index with offset = 1
        self.infos = {player_name: dict(legal_moves=self.latest_observations['player_observations']
        [int(player_name[-1])]['legal_moves_as_int'],
                                        legal_moves_as_dict=self.latest_observations['player_observations']
                                        [int(player_name[-1])]['legal_moves'],
                                        observations_vectorized=self.latest_observations['player_observations']
                                        [int(player_name[-1])]['vectorized'],
                                        observations=self.latest_observations['player_observations']
                                        [int(player_name[-1])])
                      for player_name in self.agents}
