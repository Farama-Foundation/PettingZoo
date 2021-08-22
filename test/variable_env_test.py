from pettingzoo.utils.env import AECEnv
from .example_envs import generated_agents_env_v0, generated_agents_parallel_v0
from pettingzoo.test.api_test import api_test
from pettingzoo.test.seed_test import seed_test
from pettingzoo.test.parallel_test import parallel_api_test
from pettingzoo.test.max_cycles_test import max_cycles_test
from pettingzoo.test.state_test import state_test

def test_generated_agents_aec():
    api_test(generated_agents_env_v0.env(), num_cycles=100)
    # seed_test(generated_agents_env_v0.env)

def test_generated_agents_parallel():
    parallel_api_test(generated_agents_parallel_v0.parallel_env(), num_cycles=100)
    api_test(generated_agents_parallel_v0.env(), num_cycles=100)
    seed_test(generated_agents_parallel_v0.env, num_cycles=100)
    seed_test(max_cycles_test.env)

if __name__ == "__main__":
    test_generated_agents_aec()
    test_generated_agents_parallel()
