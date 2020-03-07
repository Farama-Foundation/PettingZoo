from pettingzoo.gamma import prison
from pettingzoo.tests import api_test

env = prison.env()

api_test.api_test(env, render=True, manual_control=False)