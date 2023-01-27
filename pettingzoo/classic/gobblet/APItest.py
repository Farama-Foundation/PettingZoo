from pettingzoo.test import api_test
from pettingzoo.classic import gobblet_v1

env = gobblet_v1.env()
api_test(env, num_cycles=10, verbose_progress=False)