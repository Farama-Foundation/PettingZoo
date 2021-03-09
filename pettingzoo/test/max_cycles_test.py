def max_cycles_test(mod):
    max_cycles = 4
    parallel_env = mod.parallel_env(max_cycles=max_cycles)

    observations = parallel_env.reset()
    dones = {agent: False for agent in parallel_env.agents}
    test_cycles = max_cycles + 10  # allows environment to do more than max_cycles if it so wishes
    for step in range(test_cycles):
        actions = {agent: parallel_env.action_spaces[agent].sample() for agent in parallel_env.agents if not dones[agent]}
        observations, rewards, dones, infos = parallel_env.step(actions)
        if all(dones.values()):
            break

    pstep = step + 1

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
