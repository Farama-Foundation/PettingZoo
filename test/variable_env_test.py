from __future__ import annotations

from pettingzoo.test import api_test, parallel_api_test, seed_test
from pettingzoo.test.example_envs import (
    generated_agents_env_cust_agentid_v0,
    generated_agents_env_v0,
    generated_agents_parallel_cust_agentid_v0,
    generated_agents_parallel_v0,
)
from pettingzoo.test.seed_test import (
    check_environment_deterministic_parallel,
    parallel_seed_test,
)
from pettingzoo.utils.conversions import aec_to_parallel, parallel_to_aec


def test_generated_agents_aec():
    # check that AEC env passes API test and produces deterministic behavior
    api_test(generated_agents_env_v0.env())
    seed_test(generated_agents_env_v0.env)
    # check that AEC env using a non-string agentID passes API test and produces deterministic behavior
    api_test(generated_agents_env_cust_agentid_v0.env())
    seed_test(generated_agents_env_cust_agentid_v0.env)


def test_generated_agents_parallel():
    # check that parallel env passes API test and produces deterministic behavior
    parallel_api_test(generated_agents_parallel_v0.parallel_env())
    parallel_seed_test(generated_agents_parallel_v0.parallel_env)
    # check that parallel env using a non-string agentID passes API test and produces deterministic behavior
    parallel_api_test(generated_agents_parallel_cust_agentid_v0.parallel_env())
    parallel_seed_test(generated_agents_parallel_cust_agentid_v0.parallel_env)


def test_generated_agents_parallel_to_aec():
    # check that converting parallel env to aec passes API test and produces deterministic behavior
    # we don't do this test for aec_to_parallel because generated_agents_env_v0.env() is not parallelizable
    api_test(parallel_to_aec(generated_agents_parallel_v0.parallel_env()))
    seed_test(lambda: parallel_to_aec(generated_agents_parallel_v0.parallel_env()))

    api_test(parallel_to_aec(generated_agents_parallel_cust_agentid_v0.parallel_env()))
    seed_test(
        lambda: parallel_to_aec(
            generated_agents_parallel_cust_agentid_v0.parallel_env()
        )
    )


def test_double_conversion_equals():
    # tests that double wrapping results in the same environment
    # we don't do this test for aec_to_parallel because generated_agents_env_v0.env() is not parallelizable
    env1 = generated_agents_parallel_v0.parallel_env()
    env2 = aec_to_parallel(parallel_to_aec(generated_agents_parallel_v0.parallel_env()))
    assert type(env1) == type(
        env2
    ), f"Unequal types when double wrapped: {type(env1)} != {type(env2)}"
    check_environment_deterministic_parallel(env1, env2, 500)
