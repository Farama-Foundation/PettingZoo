from pettingzoo.butterfly import pistonball_v6

def test_core():
    env = pistonball_v6.env(n_pistons=5)
    for i in range(10):
        env.reset()
        for agent in env.agent_iter():
            observation, reward, done, info = env.last()
            if not done:
                action = env.action_space(agent).sample()
                env.step(action)
            else:
                break
