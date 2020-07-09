import random


def test_render(env):
    render_modes = env.metadata.get('render.modes')
    assert render_modes is not None, "Environment's that support rendering must define render modes in metadata"
    env.reset(observe=False)
    for mode in render_modes:
        for _ in range(10):
            for agent in env.agent_iter(env.num_agents):
                if 'legal_moves' in env.infos[agent]:
                    action = random.choice(env.infos[agent]['legal_moves'])
                else:
                    action = env.action_spaces[agent].sample()
                env.step(action, observe=False)
                env.render(mode=mode)
            env.reset()
