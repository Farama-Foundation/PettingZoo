from pettingzoo.classic import backgammon_v2

env = backgammon_v2.env()

env.reset()

obs = env.state()

