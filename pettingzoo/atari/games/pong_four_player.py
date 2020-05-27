from ..base_atari_env import BaseAtariEnv, base_env_wrapper_fn


def raw_env(**kwargs):
    return BaseAtariEnv(game="pong", num_players=4, mode_num=5, **kwargs)


env = base_env_wrapper_fn(raw_env)
