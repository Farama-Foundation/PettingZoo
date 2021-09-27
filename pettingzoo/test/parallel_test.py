import warnings

from pettingzoo.utils.conversions import from_parallel_wrapper, to_parallel_wrapper
from pettingzoo.utils.wrappers import BaseWrapper

from .api_test import missing_attr_warning


def parallel_api_test(par_env, num_cycles=10):
    if not hasattr(par_env, 'possible_agents'):
        warnings.warn(missing_attr_warning.format(name='possible_agents'))
    if not hasattr(par_env, 'observation_spaces'):
        warnings.warn(missing_attr_warning.format(name='observation_spaces'))
    if not hasattr(par_env, 'action_spaces'):
        warnings.warn(missing_attr_warning.format(name='action_spaces'))

    assert not isinstance(par_env.unwrapped, to_parallel_wrapper)
    assert not isinstance(par_env.unwrapped, from_parallel_wrapper)
    assert not isinstance(par_env.unwrapped, BaseWrapper)
    MAX_RESETS = 2
    for n_resets in range(MAX_RESETS):
        obs = par_env.reset()
        assert isinstance(obs, dict)
        assert set(obs.keys()) == (set(par_env.agents))

        done = {agent: False for agent in par_env.agents}
        live_agents = set(par_env.agents[:])
        has_finished = set()
        for i in range(num_cycles):
            actions = {agent: par_env.action_space(agent).sample() for agent in par_env.agents if agent in done and not done[agent]}
            obs, rew, done, info = par_env.step(actions)
            for agent in par_env.agents:
                if agent not in live_agents:
                    live_agents.add(agent)
            assert isinstance(obs, dict)
            assert isinstance(rew, dict)
            assert isinstance(done, dict)
            assert isinstance(info, dict)
            assert set(obs.keys()) == (set(live_agents)), "agents should not be given an observation if they were done last turn"
            assert set(rew.keys()) == (set(live_agents)), "agents should not be given a reward if they were done last turn"
            assert set(done.keys()) == (set(live_agents)), "agents should not be given a done if they were done last turn"
            assert set(info.keys()) == (set(live_agents)), "agents should not be given a info if they were done last turn"
            assert not hasattr(par_env, 'possible_agents') or set(par_env.agents).issubset(set(par_env.possible_agents)), "possible agents should include all agents always if it exists"
            for agent, d in done.items():
                if d:
                    live_agents.remove(agent)
            assert set(par_env.agents) == live_agents
            has_finished |= {agent for agent, d in done.items() if d}
            if not par_env.agents:
                assert has_finished == set(par_env.possible_agents), "not all agents finished, some were skipped over"
                break
