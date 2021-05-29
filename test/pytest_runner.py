import pytest
import pickle
from .all_modules import all_environments
from pettingzoo.test.api_test import api_test
from pettingzoo.test.seed_test import seed_test
from pettingzoo.test.parallel_test import parallel_api_test
from pettingzoo.test.max_cycles_test import max_cycles_test
from pettingzoo.test.state_test import state_test
import os


@pytest.mark.parametrize(("name", "env_module"), list(all_environments.items()))
def test_module(name, env_module):
    _env = env_module.env()
    assert str(_env) == os.path.basename(name)
    api_test(_env)
    if "classic/" not in name:
        parallel_api_test(env_module.parallel_env())

    seed_test(env_module.env, 50)

    if "classic/" not in name:
        max_cycles_test(env_module)

    if ("butterfly/" in name) or ("mpe/" in name) or ("magent/" in name):
        state_test(_env, env_module.parallel_env())

    recreated_env = pickle.loads(pickle.dumps(_env))
    api_test(recreated_env)
