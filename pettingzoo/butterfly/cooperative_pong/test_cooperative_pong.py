import warnings

import numpy as np

from pettingzoo.butterfly import cooperative_pong_v7


def _rollout(render_mode, n_cycles=30, seed=0):
    env = cooperative_pong_v7.parallel_env(render_mode=render_mode)
    observations, _ = env.reset(seed=seed)
    rng = np.random.default_rng(seed)
    frames = [(observations, env.state())]
    for _ in range(n_cycles):
        if not env.agents:
            break
        actions = {agent: int(rng.integers(3)) for agent in env.agents}
        observations, _, _, _, _ = env.step(actions)
        frames.append((observations, env.state()))
    env.close()
    return frames


def test_observations_do_not_depend_on_render_mode():
    for (obs_none, state_none), (obs_rgb, state_rgb) in zip(
        _rollout(None), _rollout("rgb_array")
    ):
        assert np.array_equal(state_none, state_rgb)
        for agent in obs_none:
            assert np.array_equal(obs_none[agent], obs_rgb[agent])


def test_observations_show_ball_and_paddles_without_render_mode():
    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter("always")
        frames = _rollout(None)
    # reset() and step() don't call render() without a render mode
    assert not [w for w in caught if "render" in str(w.message)]

    for observations, state in frames:
        # the ball and the paddles are drawn in white on a black background
        assert np.any(state == 255)
        for observation in observations.values():
            assert np.array_equal(observation, state)
    # the ball moves
    assert not np.array_equal(frames[0][1], frames[-1][1])
