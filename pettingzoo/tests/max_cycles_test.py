import warnings


def max_cycles_test(mod, name):
    if "classic/" in name:
        return
    max_cycles = 5
    parallel_env = mod.parallel_env(max_cycles=max_cycles)

    def make_policy(space):
        def sample(agent):
            return space.sample()
        return sample

    policies = {agent:make_policy(space) for agent,space in parallel_env.action_spaces.items()}
    observations = parallel_env.reset()
    dones = {agent:False for agent in parallel_env.agents}
    for step in range(max_cycles+10):
        actions = {agent: policies[agent](observations[agent]) for agent in parallel_env.agents if not dones[agent]}
        observations, rewards, dones, infos = parallel_env.step(actions)
        if all(dones.values()):
            break

    pstep = step+1

    env = mod.env(max_cycles=max_cycles)
    env.reset()
    agent1_count = 0
    agentn_count = 0
    for a in env.agent_iter():
        if a == env.possible_agents[0]:
            agent1_count += 1
        if a == env.possible_agents[-1]:
            agentn_count += 1
        action = env.action_spaces[a].sample() if not env.dones[a] else None
        env.step(action)

    assert max_cycles == pstep
    assert max_cycles == agent1_count - 1
    assert max_cycles == agentn_count - 1
