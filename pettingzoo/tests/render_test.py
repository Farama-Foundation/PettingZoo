import random
import numpy as np


def render_test(env):
    render_modes = env.metadata.get('render.modes')
    assert render_modes is not None, "Environment's that support rendering must define render modes in metadata"
    env.reset(observe=False)
    assert len(render_modes) >= 2
    for mode in render_modes:
        for agent in env.agent_iter(env.num_agents*5):
            reward, done, info = env.last()
            if not done and 'legal_moves' in env.infos[agent]:
                action = random.choice(env.infos[agent]['legal_moves'])
            else:
                action = env.action_spaces[agent].sample()
            env.step(action, observe=False)
            res = env.render(mode=mode)
            if mode == 'rgb_array':
                assert isinstance(res, np.ndarray) and len(res.shape) == 3 and res.shape[2] == 3 and res.dtype == np.uint8, "rgb_array mode must have shit in it"
            if mode == 'ansi':
                assert isinstance(res, str)# and len(res.shape) == 3 and res.shape[2] == 3 and res.dtype == np.uint8, "rgb_array mode must have shit in it"

        env.reset()
