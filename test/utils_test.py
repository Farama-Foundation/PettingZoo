from pettingzoo.utils import random_demo
from pettingzoo.classic import tictactoe_v3

def test_random_demo_without_errors():
    random_demo(tictactoe_v3.env())
