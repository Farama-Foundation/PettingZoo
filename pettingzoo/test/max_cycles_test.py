import numpy as np


def max_cycles_test(mod):
    max_cycles = 4
    parallel_env = mod.parallel_env(max_cycles=max_cycles)

    observations = parallel_env.reset()
    dones = {agent: False for agent in parallel_env.agents}
    test_cycles = max_cycles + 10  # allows environment to do more than max_cycles if it so wishes
    for step in range(test_cycles):
        actions = {agent: parallel_env.action_space(agent).sample() for agent in parallel_env.agents if not dones[agent]}
        observations, rewards, dones, infos = parallel_env.step(actions)
        if all(dones.values()):
            break

    pstep = step + 1

    env = mod.env(max_cycles=max_cycles)
    env.reset()
    agent_counts = np.zeros(len(env.possible_agents))
    for a in env.agent_iter():
        # counts agent index
        aidx = env.possible_agents.index(a)
        agent_counts[aidx] += 1

        action = env.action_space(a).sample() if not env.dones[a] else None
        env.step(action)

    assert max_cycles == pstep
    # does not check the minimum value because some agents might be killed before
    # all the steps are complete. However, most agents should still be alive
    # given a short number of cycles
    assert max_cycles == np.max(agent_counts) - 1
    assert max_cycles == np.median(agent_counts) - 1
