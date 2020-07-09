from .base_atari_env import BaseAtariEnv, base_env_wrapper_fn


def raw_env(**kwargs):
    mode = 32
    num_players = 4
    return BaseAtariEnv(game="pong", num_players=num_players, mode_num=mode, **kwargs)


env = base_env_wrapper_fn(raw_env)
