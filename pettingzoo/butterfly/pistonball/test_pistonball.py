import numpy as np
import pytest

from pettingzoo.butterfly import pistonball_v7


def _rollout(render_mode, n_cycles=20, seed=0):
    env = pistonball_v7.parallel_env(render_mode=render_mode)
    observations, _ = env.reset(seed=seed)
    rng = np.random.default_rng(seed)
    frames = [(observations, env.state())]
    for _ in range(n_cycles):
        actions = {
            agent: rng.uniform(-1, 1, size=(1,)).astype(np.float32)
            for agent in env.agents
        }
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


@pytest.mark.parametrize("render_mode", [None, "rgb_array"])
def test_observations_show_the_ball(render_mode):
    env = pistonball_v7.parallel_env(render_mode=render_mode)
    env.reset(seed=0)
    ball_color = np.array([65, 159, 221])
    ball_x, ball_y = (int(v) for v in env.unwrapped.ball.position)
    half_side = env.unwrapped.ball_radius // 2
    # most of a square inside the ball has the ball's color in the state image
    # (the rest is the line that shows the ball's rotation)
    inside_ball = env.state()[
        ball_y - half_side : ball_y + half_side, ball_x - half_side : ball_x + half_side
    ]
    assert np.mean(np.all(inside_ball == ball_color, axis=-1)) > 0.8

    initial_state = env.state()
    for _ in range(10):
        env.step({agent: np.zeros(1, dtype=np.float32) for agent in env.agents})
    # the ball falls, so the state image changes
    assert not np.array_equal(env.state(), initial_state)


def test_returned_arrays_do_not_lock_the_screen():
    env = pistonball_v7.parallel_env()
    observations, _ = env.reset(seed=0)
    held = [observations, env.state()]
    for _ in range(5):
        # drawing onto a locked surface would raise
        # "pygame.error: Surfaces must not be locked during blit"
        observations, _, _, _, _ = env.step(
            {agent: env.action_space(agent).sample() for agent in env.agents}
        )
        held.append((observations, env.state()))
