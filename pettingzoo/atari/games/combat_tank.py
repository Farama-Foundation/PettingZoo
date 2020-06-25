from ..base_atari_env import BaseAtariEnv, base_env_wrapper_fn


def raw_env(has_maze=False, is_invisible=False, billiard_hit=False, **kwargs):
    start_mapping = {
        (False, False): 1,
        (False, True): 8,
        (True, False): 10,
        (True, True): 13,
    }
    mode = start_mapping[(is_invisible, billiard_hit)] + has_maze

    return BaseAtariEnv(game="combat", num_players=2, mode_num=mode, **kwargs)


env = base_env_wrapper_fn(raw_env)
