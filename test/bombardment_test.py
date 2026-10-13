from pettingzoo.classic import rps_v2
from pettingzoo.test.bombardment_test import bombardment_test


def test_bombardment_rps():
    bombardment_test(rps_v2.env(), cycles=2)
