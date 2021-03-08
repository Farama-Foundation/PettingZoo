from pettingzoo.utils.conversions import to_parallel_wrapper, from_parallel_wrapper
from pettingzoo.utils.wrappers import BaseWrapper


def parallel_api_test(par_env, num_cycles=10):
    assert not isinstance(par_env.unwrapped, to_parallel_wrapper)
    assert not isinstance(par_env.unwrapped, from_parallel_wrapper)
    assert not isinstance(par_env.unwrapped, BaseWrapper)
    MAX_RESETS = 2
    for n_resets in range(MAX_RESETS):
        obs = par_env.reset()
        assert isinstance(obs, dict)
        assert set(obs.keys()) == (set(par_env.agents))

        done = {agent: False for agent in par_env.agents}
        live_agents = par_env.agents[:]
        has_finished = set()
        for i in range(num_cycles):
            actions = {agent: space.sample() for agent, space in par_env.action_spaces.items() if agent in done and not done[agent]}
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
            if par_env.env_done:
                assert has_finished == set(par_env.possible_agents), "not all agents finished, some were skipped over"
                break
