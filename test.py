from pettingzoo.butterfly import cooperative_pong_v2

env = cooperative_pong_v2.parallel_env()

env.reset()

obs = env.state()

