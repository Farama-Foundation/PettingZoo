from pettingzoo.classic import connect_four_v3

env = connect_four_v3.env(render_mode="human")
env.reset(seed=42)

for agent in env.agent_iter():
    observation, reward, termination, truncation, info = env.last()

    if termination or truncation:
        action = None
    else:
        mask = observation["action_mask"]
        action = env.action_space(agent).sample(
            mask
        )  # this is where you would insert your policy

    env.step(action)
env.close()
