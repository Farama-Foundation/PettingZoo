from tutorial2_adding_game_logic import CustomEnvironment
from tutorial3_action_masking import CustomActionMaskedEnvironment

from pettingzoo.test import parallel_api_test

if __name__ == "__main__":
    env = CustomEnvironment()
    parallel_api_test(env, num_cycles=1_000_000)

    env = CustomActionMaskedEnvironment()
    parallel_api_test(env, num_cycles=1_000_000)
