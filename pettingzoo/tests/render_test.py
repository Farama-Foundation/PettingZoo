import random
import numpy as np


def render_test(env):
    render_modes = env.metadata.get('render.modes')
    assert render_modes is not None, "Environment's that support rendering must define render modes in metadata"
    env.reset(observe=False)
    for mode in render_modes:
        for _ in range(10):
            for agent in env.agent_iter(env.num_agents):
                reward, done, info = env.last()
                if not done and 'legal_moves' in env.infos[agent]:
                    action = random.choice(env.infos[agent]['legal_moves'])
                else:
                    action = env.action_spaces[agent].sample()
                env.step(action, observe=False)
                res = env.render(mode=mode)
                assert isinstance(res,np.ndarray) or isinstance(res,str), "render must return numpy array containing image or a string, got {}".format(res)
