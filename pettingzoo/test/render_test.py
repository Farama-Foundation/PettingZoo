import random

import numpy as np


def collect_render_results(env):
    results = []

    env.reset()
    for i in range(5):
        if i > 0:
            for agent in env.agent_iter(env.num_agents // 2 + 1):
                obs, reward, terminated, truncated, info = env.last()
                if terminated or truncated:
                    action = None
                elif isinstance(obs, dict) and "action_mask" in obs:
                    action = random.choice(np.flatnonzero(obs["action_mask"]))
                else:
                    action = env.action_space(agent).sample()
                env.step(action)
        render_result = env.render()
        results.append(render_result)

    return results


def render_test(env_fn, custom_tests={}):
    env = env_fn(render_mode="human")
    render_modes = env.metadata.get("render_modes")[:]
    assert (
        render_modes is not None
    ), "Environments that support rendering must define render_modes in metadata"
    for mode in render_modes:
        env = env_fn(render_mode=mode)
        render_results = collect_render_results(env)
        for res in render_results:
            if mode in custom_tests.keys():
                assert custom_tests[mode](res)
            if mode == "rgb_array":
                assert (
                    isinstance(res, np.ndarray)
                    and len(res.shape) == 3
                    and res.shape[2] == 3
                    and res.dtype == np.uint8
                ), f"rgb_array mode must return a valid image array, is {res}"
            if mode == "ansi":
                assert isinstance(
                    res, str
                )  # and len(res.shape) == 3 and res.shape[2] == 3 and res.dtype == np.uint8, "rgb_array mode must have shit in it"
            if mode == "human":
                assert res is None
        env.close()
