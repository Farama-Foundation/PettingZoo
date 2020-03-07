import pettingzoo.tests.api_test as apt 


from pettingzoo.gamma import cooperative_pong

cooperative_pong = cooperative_pong.env()
apt.api_test(cooperative_pong)
