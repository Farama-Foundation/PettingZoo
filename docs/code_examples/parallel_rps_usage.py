from . import parallel_rps

env = parallel_rps.parallel_env(render_mode="human")
observations, infos = env.reset(seed=42)

while env.agents:
    # this is where you would insert your policy
    actions = {agent: env.action_space(agent).sample() for agent in env.agents}

    observations, rewards, terminations, truncations, infos = env.step(actions)
env.close()
