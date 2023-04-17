import pytest

from pettingzoo.test import api_test, parallel_api_test, seed_test
from pettingzoo.test.example_envs import (
    generated_agents_env_v0,
    generated_agents_parallel_v0,
)
from pettingzoo.test.seed_test import (
    check_environment_deterministic,
    check_environment_deterministic_parallel,
    parallel_seed_test,
)
from pettingzoo.utils.conversions import aec_to_parallel, parallel_to_aec


def test_generated_agents_aec():
    # check that that AEC env passes API test and produces deterministic behavior
    api_test(generated_agents_env_v0.env())
    seed_test(generated_agents_env_v0.env)


def test_generated_agents_parallel():
    # check that that parallel env passes API test and produces deterministic behavior
    parallel_api_test(generated_agents_parallel_v0.parallel_env())
    parallel_seed_test(lambda: generated_agents_parallel_v0.parallel_env())


def test_generated_agents_parallel_to_aec():
    # check that converting parallel env to aec passes API test and produces deterministic behavior
    api_test(generated_agents_parallel_v0.env())
    seed_test(generated_agents_parallel_v0.env)


# TODO: fix this test
@pytest.mark.skip("Failing test, incorrect rewards")
def test_parallel_generated_agents_conversions_double():
    env1 = generated_agents_parallel_v0.parallel_env()
    env2 = aec_to_parallel(parallel_to_aec(generated_agents_parallel_v0.parallel_env()))

    # ensure double-wrapped and unwrapped environments perform the same
    check_environment_deterministic_parallel(env1, env2, 500)


def test_parallel_generated_agents_conversions_triple():
    # single- and triple- wrapping should cancel out into the same underlying type
    env1 = parallel_to_aec(generated_agents_parallel_v0.parallel_env())
    env2 = parallel_to_aec(
        aec_to_parallel(parallel_to_aec(generated_agents_parallel_v0.parallel_env()))
    )
    assert type(env1) == type(
        env2
    ), "parallel_to_aec and aec_to_parallel wrappers should cancel out. Result: {type(env1)}, {type(env2)}."

    # ensure single- and triple- wrapped environments perform the same
    check_environment_deterministic(env1, env2, 500)


def test_parallel_generated_agents_conversions_quadruple():
    # double- and quadruple- wrapping should cancel out into the same underlying type
    env1 = aec_to_parallel(parallel_to_aec(generated_agents_parallel_v0.parallel_env()))
    env2 = aec_to_parallel(
        parallel_to_aec(
            aec_to_parallel(
                parallel_to_aec(generated_agents_parallel_v0.parallel_env())
            )
        )
    )
    assert type(env1) == type(
        env2
    ), "parallel_to_aec and aec_to_parallel wrappers should cancel out. Result: {type(env1)}, {type(env2)}."

    # ensure double- and quadruple- wrapped environments perform the same
    check_environment_deterministic_parallel(env1, env2, 500)


def test_parallel_generated_agents_conversions():
    # single-wrapping should produce deterministic behavior
    api_test(parallel_to_aec(generated_agents_parallel_v0.parallel_env()))

    # double-wrapping should produce deterministic behavior
    parallel_seed_test(
        lambda: aec_to_parallel(
            parallel_to_aec(generated_agents_parallel_v0.parallel_env())
        )
    )

    # triple-wrapping should produce deterministic behavior
    seed_test(
        lambda: parallel_to_aec(
            aec_to_parallel(
                parallel_to_aec(generated_agents_parallel_v0.parallel_env())
            )
        )
    )

    # quadruple-wrapping should produce deterministic behavior
    parallel_seed_test(
        lambda: aec_to_parallel(
            parallel_to_aec(
                aec_to_parallel(
                    parallel_to_aec(generated_agents_parallel_v0.parallel_env())
                )
            )
        )
    )
