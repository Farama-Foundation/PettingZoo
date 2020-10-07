
def parallel_play_test(par_env):
    obs = par_env.reset()
    assert isinstance(obs, dict)
    assert set(obs.keys()).issubset(set(par_env.agents))

    done = {agent:False for agent in par_env.agents}
    live_agents = par_env.agents[:]
    for i in range(1000):
        actions = {agent:space.sample() for agent, space in par_env.action_spaces.items() if done[agent]}
        obs, rew, done, info = par_env.step(actions)
        for agent, d in done.items():
            live_agents.remove(agent)
        assert par_env.agents == live_agents
        assert isinstance(obs, dict)
        assert isinstance(rew, dict)
        assert isinstance(done, dict)
        assert isinstance(info, dict)
        assert set(obs.keys()) == (set(par_env.agents))
        assert set(rew.keys()) == (set(par_env.agents))
        assert set(done.keys()) == (set(par_env.agents))
        assert set(info.keys()) == (set(par_env.agents))
        assert set(par_env.agents).issubset(set(par_env.possible_agents))
        if all(done.values()):
            break
