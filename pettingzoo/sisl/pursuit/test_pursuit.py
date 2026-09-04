import numpy as np
import pytest

from pettingzoo.sisl import pursuit_v6
from pettingzoo.sisl.pursuit.utils import two_d_maps


def test_state_matches_model_state():
    # use a non-square map so axis ordering mistakes are caught
    env = pursuit_v6.env(x_size=8, y_size=19, max_cycles=40)
    env.reset(seed=42)
    base_env = env.unwrapped.env
    for agent in env.agent_iter(env.num_agents * 4):
        _, _, termination, truncation, _ = env.last()
        action = None if termination or truncation else env.action_space(agent).sample()
        env.step(action)

        state = env.state()
        assert state.shape == (19, 8, 3)
        assert env.state_space.contains(state)
        assert np.array_equal(
            state, np.swapaxes(np.abs(base_env.model_state[0:3]), 2, 0)
        )


def test_observations_are_crops_of_state():
    env = pursuit_v6.env(max_cycles=40)
    env.reset(seed=0)
    base_env = env.unwrapped.env
    for agent in env.agent_iter(env.num_agents * 4):
        _, _, termination, truncation, _ = env.last()
        action = None if termination or truncation else env.action_space(agent).sample()
        env.step(action)

        state = env.state()
        for i, name in enumerate(env.agents):
            obs = env.observe(name)
            xp, yp = base_env.pursuer_layer.get_position(i)
            xlo, xhi, ylo, yhi, xolo, xohi, yolo, yohi = base_env.obs_clip(xp, yp)
            # the in-map part of each observation is a crop of the state
            assert np.array_equal(obs[yolo:yohi, xolo:xohi], state[ylo:yhi, xlo:xhi])


def test_parallel_state():
    par_env = pursuit_v6.parallel_env(max_cycles=40)
    par_env.reset(seed=42)
    state = par_env.state()
    assert par_env.state_space.contains(state)


def test_center_box_size():
    env = pursuit_v6.env(
        x_size=8,
        y_size=10,
        n_evaders=1,
        n_pursuers=1,
        center_box_size=(4, 2),
    )
    expected_map = np.zeros((8, 10), dtype=np.int32)
    expected_map[2:6, 4:6] = -1
    assert np.array_equal(env.unwrapped.env.map_matrix, expected_map)


def test_zero_center_box_size_removes_obstacle():
    env = pursuit_v6.env(
        x_size=8,
        y_size=10,
        n_evaders=1,
        n_pursuers=1,
        center_box_size=(0, 0),
    )
    assert np.count_nonzero(env.unwrapped.env.map_matrix) == 0


def test_default_center_box_size_is_unchanged():
    env = pursuit_v6.env(n_evaders=1, n_pursuers=1)
    assert np.array_equal(
        env.unwrapped.env.map_matrix,
        two_d_maps.rectangle_map(env.unwrapped.env.x_size, env.unwrapped.env.y_size),
    )


@pytest.mark.parametrize(
    ("center_box_size", "error"),
    [
        ([2, 2], TypeError),
        ((2,), TypeError),
        ((2.0, 2), TypeError),
        ((-1, 2), ValueError),
        ((9, 2), ValueError),
        ((8, 10), ValueError),
    ],
)
def test_invalid_center_box_size(center_box_size, error):
    with pytest.raises(error):
        pursuit_v6.env(
            x_size=8,
            y_size=10,
            n_evaders=1,
            n_pursuers=1,
            center_box_size=center_box_size,
        )
