from pettingzoo.butterfly import pistonball_v6
from pettingzoo.test.api_test import api_test


def test_core():
    _env = pistonball_v6.env()
    api_test(_env)
