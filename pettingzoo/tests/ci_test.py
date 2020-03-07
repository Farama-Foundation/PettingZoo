from .api_test import *


from pettingzoo.gamma import cooperative_pong

cooperative_pong = cooperative_pong.env()
api_test(cooperative_pong)
