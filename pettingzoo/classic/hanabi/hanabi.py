from pettingzoo import AECEnv

# FixMe: Complete the class documentation
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

    def _raise_error_if_config_values_out_of_range(self, kwargs):

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

    # FixMe: Implement this
    def step(self, action, observe=True):
        raise NotImplementedError

    # FixMe: Implement this
    def reset(self, observe=True):
        raise NotImplementedError

    # FixMe: Implement this
    def observe(self, agent):
        raise NotImplementedError

    # FixMe: Implement this
    def last(self):
        agent = self.agent_selection
        return self.rewards[agent], self.dones[agent], self.infos[agent]

    # FixMe: Implement this
    def render(self, mode='human'):
        raise NotImplementedError

    # FixMe: Implement this
    def close(self):
        pass
