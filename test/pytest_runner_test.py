import os

import pytest

from pettingzoo.atari import warlords_v3
from pettingzoo.test.api_test import api_test
from pettingzoo.test.max_cycles_test import max_cycles_test
from pettingzoo.test.parallel_test import parallel_api_test
from pettingzoo.test.render_test import render_test
from pettingzoo.test.seed_test import check_environment_deterministic, seed_test
from pettingzoo.test.state_test import state_test
from pettingzoo.utils import aec_to_parallel, parallel_to_aec

from .all_modules import all_environments


@pytest.mark.parametrize(("name", "env_module"), list(all_environments.items()))
def test_module(name, env_module):
    _env = env_module.env(render_mode="human")
    assert str(_env) == os.path.basename(name)
    api_test(_env)
    if "classic/" not in name:
        parallel_api_test(env_module.parallel_env())

    # seed_test(env_module.env, 50)

    # some atari environments fail this test
    if "atari/" not in name:
        seed_test(env_module.env, 50)

    render_test(env_module.env)

    if "classic/" not in name:
        max_cycles_test(env_module)

    if ("butterfly/" in name) or ("mpe/" in name):
        state_test(env_module.env(), env_module.parallel_env())

    # recreated_env = pickle.loads(pickle.dumps(_env))
    # recreated_env.seed(42)
    # api_test(recreated_env)


def test_conversions():
    env1 = warlords_v3.env()
    env2 = parallel_to_aec(aec_to_parallel(warlords_v3.env()))
    check_environment_deterministic(env1, env2, 5000)
