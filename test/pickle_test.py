from __future__ import annotations

import pickle

import pytest
from gymnasium.utils.env_checker import data_equivalence

from pettingzoo.test.seed_test import seed_action_spaces, seed_observation_spaces
from pettingzoo.utils.all_modules import all_environments

ALL_ENVS = list(all_environments.items())


@pytest.mark.parametrize(("name", "env_module"), ALL_ENVS)
def test_pickle_env(name, env_module):
    env1 = env_module.env(render_mode="human")
    env2 = pickle.loads(pickle.dumps(env1))

    env1.reset(seed=42)
    env2.reset(seed=42)

    seed_action_spaces(env1)
    seed_action_spaces(env2)
    seed_observation_spaces(env1)
    seed_observation_spaces(env2)

    iter = 0
    for agent1, agent2 in zip(env1.agent_iter(), env2.agent_iter()):
        if iter > 10:
            break
        assert data_equivalence(agent1, agent2), f"Incorrect agent: {agent1} {agent2}"

        obs1, rew1, term1, trunc1, info1 = env1.last()
        obs2, rew2, term2, trunc2, info2 = env2.last()

        if term1 or term2 or trunc1 or trunc2:
            break

        assert data_equivalence(obs1, obs2), f"Incorrect observations: {obs1} {obs2}"
        assert data_equivalence(rew1, rew2), f"Incorrect rewards: {rew1} {rew2}"
        assert data_equivalence(term1, term2), f"Incorrect terms: {term1} {term2}"
        assert data_equivalence(trunc1, trunc2), f"Incorrect truncs: {trunc1} {trunc2}"
        assert data_equivalence(info1, info2), f"Incorrect info: {info1} {info2}"

        mask = None
        if "action_mask" in info1:
            mask = info1["action_mask"]

        if isinstance(obs1, dict) and "action_mask" in obs1:
            mask = obs1["action_mask"]

        action1 = env1.action_space(agent1).sample(mask=mask)
        action2 = env2.action_space(agent2).sample(mask=mask)

        assert data_equivalence(
            action1, action2
        ), f"Incorrect actions: {action1} {action2}"

        env1.step(action1)
        env2.step(action2)
        iter += 1
    env1.close()
    env2.close()
