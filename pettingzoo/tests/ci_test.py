from api_test import api_test


from pettingzoo.gamma import cooperative_pong

cooperative_pong = cooperative_pong.env()
api_test.api_test(cooperative_pong)