# from tutorial3_action_masking import CustomEnvironment  # relative import (not recommended)
from tutorials.EnvironmentCreation.tutorial3_action_masking import CustomEnvironment

from pettingzoo.test import parallel_api_test

if __name__ == "__main__":
    env = CustomEnvironment()
    parallel_api_test(env, num_cycles=1_000_000)
