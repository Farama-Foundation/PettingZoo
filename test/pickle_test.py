import pickle

import pytest
from gymnasium.utils.env_checker import data_equivalence

from .all_modules import all_environments

ALL_ENVS = list(all_environments.items())
FAILING_ENV_NAMES = ["mpe/simple_world_comm_v2"]
PASSING_ENVS = [
    (name, env_module)
    for (name, env_module) in ALL_ENVS
    if name not in FAILING_ENV_NAMES
]


@pytest.mark.parametrize(("name", "env_module"), PASSING_ENVS)
def test_pickle_env(name, env_module):
    env1 = env_module.env(render_mode=None)
    env2 = pickle.loads(pickle.dumps(env1))

    env1.reset(seed=42)
    env2.reset(seed=42)

    agent1 = env1.agents[0]
    agent2 = env2.agents[0]

    a_space1 = env1.action_space(agent1)
    a_space1.seed(42)
    a_space2 = env2.action_space(agent2)
    a_space2.seed(42)

    iter = 0
    for agent1, agent2 in zip(env1.agent_iter(), env2.agent_iter()):
        if iter > 10:
            break
        assert data_equivalence(agent1, agent2), f"Incorrect agent: {agent1} {agent2}"

        obs1, rew1, term1, trunc1, info1 = env1.last()
        obs2, rew2, term2, trunc2, info2 = env2.last()

        if name == "mpe/simple_world_comm_v2":
            print("Test")

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

        action1 = a_space1.sample(mask=mask)
        action2 = a_space2.sample(mask=mask)

        assert data_equivalence(
            action1, action2
        ), f"Incorrect actions: {action1} {action2}"

        env1.step(action1)
        env2.step(action2)
        iter += 1
    env1.close()
    env2.close()
