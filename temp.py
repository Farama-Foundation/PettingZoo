from pettingzoo.sisl import multiwalker_v8
env = multiwalker_v8.env()

env.reset()
for episode in range(100000):
    for agent in env.agent_iter():
        _, _, done, _ = env.last()
        action = env.action_space(agent).sample() if not done else None
        env.step(action)
        env.render()
