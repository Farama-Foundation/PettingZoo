from pettingzoo.test.api_test import api_test
from pettingzoo.test.example_envs import (
    generated_agents_env_v0,
    generated_agents_parallel_v0,
)
from pettingzoo.test.parallel_test import parallel_api_test
from pettingzoo.test.seed_test import check_environment_deterministic
from pettingzoo.utils.conversions import aec_to_parallel, parallel_to_aec


def test_generated_agents_aec():
    api_test(generated_agents_env_v0.env())
    # seed_test(generated_agents_env_v0.env)


def test_generated_agents_parallel():
    parallel_api_test(generated_agents_parallel_v0.parallel_env())
    api_test(generated_agents_parallel_v0.env())
    # seed_test(generated_agents_parallel_v0.env)
    # seed_test(generated_agents_parallel_v0.env)


def test_parallel_generated_agents_conversions():
    parallel_api_test(aec_to_parallel(generated_agents_parallel_v0.env()))
    api_test(parallel_to_aec(generated_agents_parallel_v0.parallel_env()))

    env1 = parallel_to_aec(generated_agents_parallel_v0.parallel_env())
    env2 = parallel_to_aec(
        aec_to_parallel(parallel_to_aec(generated_agents_parallel_v0.parallel_env()))
    )
    check_environment_deterministic(env1, env2, 500)


if __name__ == "__main__":
    test_generated_agents_aec()
    test_generated_agents_parallel()
