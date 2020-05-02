from pettingzoo.utils import save_observation

def test_observe(env, observation_0, save_obs):
    for agent in env.agent_order:
        observation = env.observe(agent)
        if save_obs:
            save_observation(env=env, agent=agent, save_dir="saved_observations")
        test_obervation(observation, observation_0)
