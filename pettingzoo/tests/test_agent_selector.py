
def test_agent_selector(env):
    if not hasattr(env, "_agent_selector"):
        warnings.warn("Env has no object named _agent_selector. We recommend handling agent cycling with the agent_selector utility from utils/agent_selector.py.")
        return

    if not isinstance(env._agent_selector, agent_selector):
        warnings.warn("You created your own agent_selector utility. You might want to use ours, in utils/agent_selector.py")
        return

    assert hasattr(env, "agent_order"), "Env does not have agent_order"

    env.reset(observe=False)
    agent_order = copy(env.agent_order)
    _agent_selector = agent_selector(agent_order)
    agent_selection = _agent_selector.next()
    assert env._agent_selector == _agent_selector, "env._agent_selector is initialized incorrectly"
    assert env.agent_selection == agent_selection, "env.agent_selection is not the same as the first agent in agent_order"

    for _ in range(200):
        agent = agent_selection
        if 'legal_moves' in env.infos[agent]:
            action = random.choice(env.infos[agent]['legal_moves'])
        else:
            action = env.action_spaces[agent].sample()
        env.step(action, observe=False)

        if all(env.dones.values()):
            break

        if agent_order == env.agent_order:
            agent_selection = _agent_selector.next()
            assert env.agent_selection == agent_selection, "env.agent_selection ({}) is not the same as the next agent in agent_order {}".format(env.agent_selection, env.agent_order)
        else:
            previous_agent_selection_index = agent_order.index(agent_selection)
            agent_order = copy(env.agent_order)
            _agent_selector.reinit(agent_order)
            skips = (previous_agent_selection_index + 1) % len(env.agents)
            for _ in range(skips + 1):
                agent_selection = _agent_selector.next()
            assert env.agent_selection == agent_selection, "env.agent_selection ({}) is not the same as the next agent in agent_order {}".format(env.agent_selection, env.agent_order)
