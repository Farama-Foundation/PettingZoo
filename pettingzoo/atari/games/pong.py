from ..base_atari_env import BaseAtariEnv, base_env_wrapper_fn

def raw_env(**kwargs):
    return BaseAtariEnv("pong", 2, **kwargs)

env = base_env_wrapper_fn(raw_env)
