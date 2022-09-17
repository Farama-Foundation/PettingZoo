from docs.code_examples import aec_rps, parallel_rps
from pettingzoo.test import api_test, parallel_api_test


def test_rps_aec_example():
    api_test(aec_rps.raw_env(), 100)
    api_test(aec_rps.env(), 100)


def test_rps_parallel_example():
    print(type(parallel_rps.raw_env()))
    print(type(parallel_rps.raw_env().env))
    parallel_api_test(parallel_rps.parallel_env(), 100)
    api_test(parallel_rps.raw_env(), 100)
    api_test(parallel_rps.env(), 100)
