
def parallel_play_test(par_env):
    obs = par_env.reset()
    assert isinstance(obs, dict)
    assert set(obs.keys()) == (set(par_env.agents))

    done = {agent:False for agent in par_env.agents}
    live_agents = par_env.agents[:]
    has_finished = set()
    num_resets = 0
    for i in range(1000):
        actions = {agent:space.sample() for agent, space in par_env.action_spaces.items() if agent in done and not done[agent]}
        obs, rew, done, info = par_env.step(actions)
        assert par_env.agents == live_agents
        assert isinstance(obs, dict)
        assert isinstance(rew, dict)
        assert isinstance(done, dict)
        assert isinstance(info, dict)
        assert set(obs.keys()) == (set(par_env.agents)), "agents should not be given an observation if they were done last turn"
        assert set(rew.keys()) == (set(par_env.agents)), "agents should not be given a reward if they were done last turn"
        assert set(done.keys()) == (set(par_env.agents)), "agents should not be given a done if they were done last turn"
        assert set(info.keys()) == (set(par_env.agents)), "agents should not be given a info if they were done last turn"
        assert set(par_env.agents).issubset(set(par_env.possible_agents)), "possible agents should include all agents always"
        for agent, d in done.items():
            if d:
                live_agents.remove(agent)
        has_finished |= {agent for agent, d in done.items() if d}
        if not done or i % 200 == 199:
            if not done:
                assert has_finished == set(par_env.possible_agents), "not all agents finished, some were skipped over"
            obs = par_env.reset()

            done = {agent:False for agent in par_env.agents}
            live_agents = par_env.agents[:]
            has_finished = set()
            if num_resets > 0:
                break
            num_resets += 1
