import pytest
from gymnasium import spaces
from gymnasium.utils.env_checker import data_equivalence

from pettingzoo.test import api_test
from pettingzoo.utils import conversions, wrappers

from .all_modules import all_environments


def box_action(env, agents):
    boxable = True
    for agent in agents:
        boxable = boxable and isinstance(env.action_space(agent), spaces.Box)
    return boxable


def box_observation(env, agents):
    boxable = True
    for agent in agents:
        boxable = boxable and isinstance(env.observation_space(agent), spaces.Box)
    return boxable


def discrete_observation(env, agents):
    is_discrete = True
    for agent in agents:
        is_discrete = is_discrete and (
            isinstance(env.observation_space(agent), spaces.Discrete)
        )
    return is_discrete


@pytest.mark.parametrize(("name", "env_module"), list(all_environments.items()))
def test_unwrapped(name, env_module):
    env = env_module.env(render_mode="human")
    base_env = env.unwrapped

    env.reset()
    agents = env.agents

    if discrete_observation(env, agents):
        env = wrappers.AssertOutOfBoundsWrapper(env)
    env = wrappers.BaseWrapper(env)
    env = wrappers.CaptureStdoutWrapper(env)
    if box_observation(env, agents) and box_action(env, agents):
        env = wrappers.ClipOutOfBoundsWrapper(env)
    env = wrappers.OrderEnforcingWrapper(env)
    env = wrappers.TerminateIllegalWrapper(env, 1.0)

    if env.metadata["is_parallelizable"]:
        env = conversions.aec_to_parallel(env)

    env = conversions.parallel_to_aec(env)
    env = conversions.turn_based_aec_to_parallel(env)

    assert env.unwrapped == base_env, "Unwrapped Test: unequal envs"


@pytest.mark.parametrize(("name", "env_module"), list(all_environments.items()))
def test_base_wrapper(name, env_module, num_cycles=100):
    env = env_module.env(render_mode=None)
    env.reset()
    wrapped_env = wrappers.BaseWrapper(env)
    wrapped_env.last()  # Tests attributes accessibility

    api_test(
        wrapped_env, num_cycles=num_cycles
    )  # BaseWrapper(env) should pass api test

    # BaseWrapper(env) and env must behave in the same way given the same seeds.
    env = env_module.env(render_mode=None)
    wrapped_env = wrappers.BaseWrapper(env_module.env(render_mode=None))
    env.reset(seed=42)
    wrapped_env.reset(seed=42)
    for agent in env.agents:
        env.action_space(agent).seed(42)
        wrapped_env.action_space(agent).seed(42)

    cycle = 0
    for agent1, agent2 in zip(env.agent_iter(), wrapped_env.agent_iter()):
        if cycle > num_cycles:
            break
        assert data_equivalence(agent1, agent2), f"Incorrect agent: {agent1} {agent2}"

        obs1, rew1, term1, trunc1, info1 = env.last()
        obs2, rew2, term2, trunc2, info2 = wrapped_env.last()

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

        action1 = env.action_space(env.agent_selection).sample(mask=mask)
        action2 = wrapped_env.action_space(wrapped_env.agent_selection).sample(
            mask=mask
        )

        assert data_equivalence(
            action1, action2
        ), f"Incorrect actions: {action1} {action2}"

        env.step(action1)
        wrapped_env.step(action2)
        cycle += 1
    env.close()
    wrapped_env.close()
