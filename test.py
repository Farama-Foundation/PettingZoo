from pettingzoo.mpe import simple_adversary_v2

env = simple_adversary_v2.env()
env.reset()

print(env.state().shape)