import pytest
import pickle
from .all_modules import all_environments
import pettingzoo.tests.api_test as api_test

from .error_tests import error_test
from .seed_test import seed_test
from .render_test import render_test
from .parallel_test import parallel_play_test


@pytest.mark.parametrize(("name", "env_module"), list(all_environments.items()))
def test_module(name, env_module):
    _env = env_module.env()
    api_test.api_test(_env)
    if "classic/" not in name:
        parallel_play_test(env_module.parallel_env())

    seed_test(env_module.env)

    # pickle test
    env2 = pickle.loads(pickle.dumps(_env))
    api_test.api_test(env2)
    # render_test(_env)
    # error_test(env_module.env())
