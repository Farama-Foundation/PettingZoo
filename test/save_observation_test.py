import numpy as np
import pytest
from gymnasium.spaces import Box
from PIL import Image

from pettingzoo.utils import save_observation

from .color_reduction_test import AGENTS, DummyAEC


@pytest.mark.parametrize(
    "shape", [(2, 3), (2, 3, 3), (2, 3, 1), (1, 3, 1), (2, 1, 1), (1, 1, 1)]
)
def test_save_observation_preserves_image_pixels(tmp_path, shape):
    observation = np.arange(np.prod(shape)).reshape(shape).astype(np.uint8)
    env = DummyAEC(
        Box(0, 255, shape=shape, dtype=np.uint8),
        dict.fromkeys(AGENTS, observation),
    )
    env.reset()

    save_observation(env, save_dir=str(tmp_path))

    one_channel = len(shape) == 3 and shape[2] == 1
    expected = observation[:, :, 0] if one_channel else observation
    with Image.open(tmp_path / str(env) / f"{env.agent_selection}.png") as image:
        assert image.mode == ("RGB" if len(shape) == 3 and shape[2] == 3 else "L")
        np.testing.assert_array_equal(np.asarray(image), expected)
