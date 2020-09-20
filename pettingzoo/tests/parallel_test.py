
def parallel_play_test(par_env):
    obs = par_env.reset()
    assert isinstance(obs, dict)
    assert set(obs.keys()).issubset(set(par_env.agents))

    for i in range(1000):
        actions = {agent:space.sample() for agent, space in par_env.action_spaces.items()}
        obs, rew, done, info = par_env.step(actions)
        assert isinstance(obs, dict)
        assert isinstance(rew, dict)
        assert isinstance(done, dict)
        assert isinstance(info, dict)
        assert set(obs.keys()).issubset(set(par_env.agents))
        assert set(rew.keys()).issubset(set(par_env.agents))
        assert set(done.keys()).issubset(set(par_env.agents))
        assert set(info.keys()).issubset(set(par_env.agents))
        if all(done.values()):
            break
