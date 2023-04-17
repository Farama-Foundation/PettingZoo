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
    api_test(generated_agents_env_v0.env())
    seed_test(generated_agents_env_v0.env)


def test_generated_agents_parallel():
    parallel_api_test(generated_agents_parallel_v0.parallel_env())
    parallel_seed_test(lambda: generated_agents_parallel_v0.parallel_env())


@pytest.mark.skip(
    reason="parallel_to_aec wrapper produces nondeterministic behavior with this environment."
)
def test_generated_agents_parallel_to_aec():
    api_test(generated_agents_parallel_v0.env())
    # seed_test(generated_agents_parallel_v0.env)


def test_parallel_generated_agents_conversions():
    parallel_api_test(aec_to_parallel(generated_agents_parallel_v0.env()))
    api_test(parallel_to_aec(generated_agents_parallel_v0.parallel_env()))

    # double-wrapping should produce the same behavior as unwrapped env
    env1 = generated_agents_parallel_v0.parallel_env()
    env2 = aec_to_parallel(parallel_to_aec(generated_agents_parallel_v0.parallel_env()))

    # fails (due to parallel_to_aec conversion issues with this environment)
    # check_environment_deterministic_parallel(env1, env2, 500)

    # double-wrapping should produce deterministic behavior
    parallel_seed_test(
        lambda: aec_to_parallel(
            parallel_to_aec(generated_agents_parallel_v0.parallel_env())
        )
    )

    # double- and quadruple- wrapping should cancel out in the same way
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


@pytest.mark.skip(
    reason="parallel_to_aec wrapper produces nondeterministic behavior with this environment."
)
def test_parallel_generated_agents_conversions_aec():
    # fails
    seed_test(
        lambda: parallel_to_aec(
            aec_to_parallel(
                parallel_to_aec(generated_agents_parallel_v0.parallel_env())
            )
        )
    )

    # single- and triple-wrapping should cancel out in the same way
    env1 = parallel_to_aec(generated_agents_parallel_v0.parallel_env())
    env2 = parallel_to_aec(
        aec_to_parallel(parallel_to_aec(generated_agents_parallel_v0.parallel_env()))
    )
    assert type(env1) == type(
        env2
    ), "parallel_to_aec and aec_to_parallel wrappers should cancel out. Result: {type(env1)}, {type(env2)}."

    # fails because using parallel_to_aec with this environment can produce nondeterministic behavior
    check_environment_deterministic(env1, env2, 500)
