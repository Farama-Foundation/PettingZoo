import pytest
import pickle
from .all_modules import all_environments
from .api_test import api_test
from .seed_test import seed_test
from .render_test import render_test
from .parallel_test import parallel_play_test
from .max_cycles_test import max_cycles_test


@pytest.mark.parametrize(("name", "env_module"), list(all_environments.items()))
def test_module(name, env_module):
    _env = env_module.env()
    api_test(_env)
    if "classic/" not in name:
        parallel_play_test(env_module.parallel_env())

    if "prospector" not in name:
        seed_test(env_module.env, 50)

    max_cycles_test(env_module, name)

    recreated_env = pickle.loads(pickle.dumps(_env))
    api_test(recreated_env)
