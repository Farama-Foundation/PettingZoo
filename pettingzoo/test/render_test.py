import random
import numpy as np


def render_test(env):
    render_modes = env.metadata.get('render.modes')
    assert render_modes is not None, "Environment's that support rendering must define render modes in metadata"
    env.reset()
    assert len(render_modes) >= 2
    for mode in render_modes:
        assert (mode in {"human", "ansi", "rgb_array"})
        env.reset()
        for i in range(5):
            if i > 0:
                for agent in env.agent_iter(env.num_agents // 2 + 1):
                    obs, reward, done, info = env.last()
                    if done:
                        action = None
                    elif isinstance(obs, dict) and 'action_mask' in obs:
                        action = random.choice(np.flatnonzero(obs['action_mask']))
                    else:
                        action = env.action_spaces[agent].sample()
                    env.step(action)
            res = env.render(mode=mode)
            if mode == 'rgb_array':
                assert isinstance(res, np.ndarray) and len(res.shape) == 3 and res.shape[2] == 3 and res.dtype == np.uint8, f"rgb_array mode must return a valid image array, is {res}"
            if mode == 'ansi':
                assert isinstance(res, str)  # and len(res.shape) == 3 and res.shape[2] == 3 and res.dtype == np.uint8, "rgb_array mode must have shit in it"
            if mode == "human":
                assert res is None
        env.reset()
    env.close()
