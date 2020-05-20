import pytest
from .all_modules import all_environments
import pettingzoo.tests.api_test as api_test

from .error_tests import error_test
from .seed_test import seed_test
from .render_test import test_render


@pytest.mark.parametrize("env_module", list(all_environments.values()))
def test_module(env_module):
    _env = env_module.env()
    api_test.api_test(_env)

    seed_test(env_module.env)
    # test_render(_env)
    # error_test(env_module.env())
