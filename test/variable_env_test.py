from pettingzoo.utils.env import AECEnv
from pettingzoo.test.example_envs import generated_agents_env_v0, generated_agents_parallel_v0
from pettingzoo.test.api_test import api_test
from pettingzoo.test.seed_test import seed_test, check_environment_deterministic
from pettingzoo.test.parallel_test import parallel_api_test
from pettingzoo.test.max_cycles_test import max_cycles_test
from pettingzoo.test.state_test import state_test
from pettingzoo.utils.conversions import aec2parallel, parallel2aec


def test_generated_agents_aec():
    api_test(generated_agents_env_v0.env(), num_cycles=300)
    # seed_test(generated_agents_env_v0.env)


def test_generated_agents_parallel():
    parallel_api_test(generated_agents_parallel_v0.parallel_env(), num_cycles=300)
    api_test(generated_agents_parallel_v0.env(), num_cycles=300)
    # seed_test(generated_agents_parallel_v0.env, num_cycles=300)
    # seed_test(generated_agents_parallel_v0.env)


def test_parallel_generated_agents_conversions():
    parallel_api_test(aec2parallel(generated_agents_parallel_v0.env()), num_cycles=300)
    api_test(parallel2aec(generated_agents_parallel_v0.parallel_env()), num_cycles=300)

    env1 = parallel2aec(generated_agents_parallel_v0.parallel_env())
    env2 = parallel2aec(aec2parallel(parallel2aec(generated_agents_parallel_v0.parallel_env())))
    check_environment_deterministic(env1, env2, 500)


if __name__ == "__main__":
    test_generated_agents_aec()
    test_generated_agents_parallel()
