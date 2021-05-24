from .base_atari_env import BaseAtariEnv, base_env_wrapper_fn, parallel_wrapper_fn
import os


def raw_env(**kwargs):
    mode = 33
    num_players = 4
    return BaseAtariEnv(game="pong", num_players=num_players, mode_num=mode, env_name=os.path.basename(__file__)[:-3], **kwargs)


env = base_env_wrapper_fn(raw_env)
parallel_env = parallel_wrapper_fn(env)
