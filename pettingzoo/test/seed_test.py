from __future__ import annotations

from gymnasium.utils.env_checker import data_equivalence


def seed_action_spaces(env):
    if hasattr(env, "agents"):
        for i, agent in enumerate(env.agents):
            env.action_space(agent).seed(42 + i)


def seed_observation_spaces(env):
    if hasattr(env, "agents"):
        for i, agent in enumerate(env.agents):
            env.observation_space(agent).seed(42 + i)


def check_environment_deterministic(env1, env2, num_cycles):
    """Check that two AEC environments execute the same way."""

    env1.reset(seed=42)
    env2.reset(seed=42)

    # seed action spaces to ensure sampled actions are the same
    seed_action_spaces(env1)
    seed_action_spaces(env2)

    # seed observation spaces to ensure first observation is the same
    seed_observation_spaces(env1)
    seed_observation_spaces(env2)

    iter = 0
    max_env_iters = num_cycles * len(env1.agents)

    for agent1, agent2 in zip(env1.agent_iter(), env2.agent_iter()):
        assert data_equivalence(agent1, agent2), f"Incorrect agent: {agent1} {agent2}"

        obs1, reward1, termination1, truncation1, info1 = env1.last()
        obs2, reward2, termination2, truncation2, info2 = env2.last()

        assert data_equivalence(obs1, obs2), "Incorrect observation"
        assert data_equivalence(reward1, reward2), "Incorrect reward."
        assert data_equivalence(termination1, termination2), "Incorrect termination."
        assert data_equivalence(truncation1, truncation2), "Incorrect truncation."
        assert data_equivalence(info1, info2), "Incorrect info."

        if termination1 or truncation1:
            break

        mask1 = (
            obs1.get("action_mask")
            if (isinstance(obs1, dict) and "action_mask" in obs1)
            else (info1.get("action_mask") if "action_mask" in info1 else None)
        )
        mask2 = (
            obs2.get("action_mask")
            if (isinstance(obs2, dict) and "action_mask" in obs2)
            else (info2.get("action_mask") if "action_mask" in info2 else None)
        )

        assert data_equivalence(mask1, mask2), f"Incorrect action mask: {mask1} {mask2}"

        action1 = env1.action_space(agent1).sample(mask1)
        action2 = env2.action_space(agent2).sample(mask2)

        assert data_equivalence(
            action1, action2
        ), f"Incorrect actions: {action1} {action2}"

        env1.step(action1)
        env2.step(action2)

        iter += 1

        if iter >= max_env_iters:
            break

    env1.close()
    env2.close()


def check_environment_deterministic_parallel(env1, env2, num_cycles):
    """Check that two parallel environments execute the same way."""
    env1.reset(seed=42)
    env2.reset(seed=42)

    # seed action spaces to ensure sampled actions are the same
    seed_action_spaces(env1)
    seed_action_spaces(env2)

    # seed observation spaces to ensure first observation is the same
    seed_observation_spaces(env1)
    seed_observation_spaces(env2)

    iter = 0
    max_env_iters = num_cycles * len(env1.agents)

    env1.reset(seed=42)
    env2.reset(seed=42)

    seed_action_spaces(env1)
    seed_action_spaces(env2)

    while env1.agents:
        actions1 = {agent: env1.action_space(agent).sample() for agent in env1.agents}
        actions2 = {agent: env2.action_space(agent).sample() for agent in env2.agents}

        assert data_equivalence(actions1, actions2), "Incorrect action seeding"

        obs1, rewards1, terminations1, truncations1, infos1 = env1.step(actions1)
        obs2, rewards2, terminations2, truncations2, infos2 = env2.step(actions2)

        iter += 1

        assert data_equivalence(obs1, obs2), "Incorrect observations"
        assert data_equivalence(rewards1, rewards2), "Incorrect values for rewards"
        assert data_equivalence(terminations1, terminations2), "Incorrect terminations."
        assert data_equivalence(truncations1, truncations2), "Incorrect truncations"
        assert data_equivalence(infos1, infos2), "Incorrect infos"

        if iter >= max_env_iters or any(terminations1) or any(truncations1):
            break

    env1.close()
    env2.close()


def seed_test(env_constructor, num_cycles=500):
    env1 = env_constructor()
    env2 = env_constructor()

    check_environment_deterministic(env1, env2, num_cycles)


def parallel_seed_test(parallel_env_fn, num_cycles=500):
    env1 = parallel_env_fn()
    env2 = parallel_env_fn()

    check_environment_deterministic_parallel(env1, env2, num_cycles)
