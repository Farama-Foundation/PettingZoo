from .base_atari_env import BaseAtariEnv, base_env_wrapper_fn, parallel_wrapper_fn
import os


def raw_env(alternating_control=False, moving_shields=True, zigzaging_bombs=False, fast_bomb=False, invisible_invaders=False, **kwargs):
    mode = 33 + (
        moving_shields * 1
        + zigzaging_bombs * 2
        + fast_bomb * 4
        + invisible_invaders * 8
        + alternating_control * 16
    )
    return BaseAtariEnv(game="space_invaders", num_players=2, mode_num=mode, env_name=os.path.basename(__file__)[:-3], **kwargs)


env = base_env_wrapper_fn(raw_env)
parallel_env = parallel_wrapper_fn(env)
