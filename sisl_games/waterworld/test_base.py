from .waterworld_base import MAWaterWorld

env = MAWaterWorld()
obs = env.reset()
done = False

while not done:
    obs, rew, dones, _ = env.step(env.np_random.randn(10) * .5)
    if rew.sum() > 0:
        print("Reward = ", rew)
    done = any(dones)
    env.render()
    
env.close()
