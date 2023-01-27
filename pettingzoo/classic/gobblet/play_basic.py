from pettingzoo.classic import gobblet_v1

env = gobblet_v1.env(render_mode="human_full")
env.reset()
for agent in env.agent_iter():
    observation, reward, termination, truncation, info = env.last()
    action = None if termination or truncation else env.action_space(agent).sample()  # this is where you would insert your policy
    if not termination and not truncation:
        pos = action % 9; piece = (action // 9) + 1
        print(f"AGENT: {agent}, ACTION: {action}, POSITION: {pos}, PIECE: {piece}")

    env.step(action)

