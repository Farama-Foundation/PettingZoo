from .base_atari_env import BaseAtariEnv, base_env_wrapper_fn


def raw_env(is_jet=False, guided_missile=False, **kwargs):
    mode = (21 if is_jet else 15) + (0 if guided_missile else 1)

    return BaseAtariEnv(game="combat", num_players=2, mode_num=mode, **kwargs)


env = base_env_wrapper_fn(raw_env)
