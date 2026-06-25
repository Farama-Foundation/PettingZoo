from __future__ import annotations

import numpy as np
import pygame
import pytest

from pettingzoo.butterfly import (
    cooperative_pong_v6,
    knights_archers_zombies_v11,
    pistonball_v6,
)
from pettingzoo.classic import (
    chess_v6,
    connect_four_v3,
    gin_rummy_v4,
    go_v5,
    leduc_holdem_v4,
    rps_v2,
    texas_holdem_v4,
    tictactoe_v3,
)
from pettingzoo.sisl import multiwalker_v9, pursuit_v4

pygame_envs = [
    cooperative_pong_v6,
    knights_archers_zombies_v11,
    pistonball_v6,
    chess_v6,
    connect_four_v3,
    gin_rummy_v4,
    go_v5,
    leduc_holdem_v4,
    rps_v2,
    texas_holdem_v4,
    tictactoe_v3,
    multiwalker_v9,
    pursuit_v4,
]


@pytest.mark.parametrize("env_module", pygame_envs)
def test_no_pygame_subsystem_init_without_rendering(env_module):
    # Constructing and stepping an environment that is not being rendered
    # should not initialize any pygame subsystem: full pygame.init() starts
    # the audio/joystick subsystems, and enumerating audio devices can take
    # several seconds on some platforms (https://github.com/Farama-Foundation/PettingZoo/issues/1252).
    pygame.quit()
    env = env_module.env(render_mode=None)
    env.reset(seed=42)
    for agent in env.agent_iter(max_iter=4):
        obs, reward, termination, truncation, info = env.last()
        action = (
            None
            if termination or truncation
            else env.action_space(agent).sample(
                obs["action_mask"] if isinstance(obs, dict) else None
            )
        )
        env.step(action)
    assert pygame.display.get_init() is False
    assert pygame.mixer.get_init() is None
    assert pygame.font.get_init() is False
    env.close()


@pytest.mark.parametrize("env_module", pygame_envs)
def test_rgb_array_render_does_not_init_audio(env_module):
    # Rendering only needs the display (and font) subsystems, never audio.
    pygame.quit()
    env = env_module.env(render_mode="rgb_array")
    env.reset(seed=42)
    frame = env.render()
    assert isinstance(frame, np.ndarray) and frame.size > 0
    assert pygame.mixer.get_init() is None
    env.close()
